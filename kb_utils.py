"""
kb_utils.py — 多智能体系统的 RAG 知识库模块

复用项目一的 BM25 检索 + 商品数据，为多智能体提供：
  - 文档知识库检索（PDF/TXT/MD/DOCX）
  - 商品检索（复用 products.json）
  - 融合检索（文档片段 + 商品信息统一检索）
  - 库存预警

V2 新增: RAG（检索增强生成）能力
"""

import os
import sys
import io
import re
import math
import json
from pathlib import Path
from collections import Counter
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    os.environ["PYTHONIOENCODING"] = "utf-8"

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCUMENTS_DIR = os.path.join(BASE_DIR, "documents")
STATE_FILE = os.path.join(BASE_DIR, "knowledge_base.json")

# 复用项目一的 products.json
_PROJECT1_ROOT = os.path.dirname(BASE_DIR)  # ai-knowledge-assistant
PRODUCTS_FILE = os.path.join(_PROJECT1_ROOT, "products.json")


# =====================================================================
#  文档加载
# =====================================================================

def load_document(file_path: str) -> str:
    path_lower = file_path.lower()
    if path_lower.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        texts = []
        for page in reader.pages:
            t = page.extract_text()
            if t and t.strip():
                texts.append(t.strip())
        return "\n\n".join(texts)
    elif path_lower.endswith(".docx"):
        from docx import Document
        doc = Document(file_path)
        texts = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(texts)
    else:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()


# =====================================================================
#  文本切分
# =====================================================================

def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    if not text or not text.strip():
        return []
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[str] = []
    current = ""
    for para in paragraphs:
        if current and len(current) + len(para) + 2 <= chunk_size:
            current += "\n\n" + para
            continue
        if current:
            chunks.append(current)
            current = ""
        if len(para) > chunk_size:
            sentences = re.split(r'(?<=[。！？.!?])', para)
            sent_buf = ""
            for sent in sentences:
                sent = sent.strip()
                if not sent:
                    continue
                if not sent_buf:
                    sent_buf = sent
                elif len(sent_buf) + len(sent) + 1 <= chunk_size:
                    sent_buf += sent
                else:
                    chunks.append(sent_buf)
                    sent_buf = sent
            if sent_buf:
                chunks.append(sent_buf)
        else:
            chunks.append(para)
    if current:
        chunks.append(current)
    return chunks


# =====================================================================
#  BM25 检索器
# =====================================================================

class BM25:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.docs: List[str] = []
        self.metadatas: List[Dict] = []
        self.avg_doc_len = 0.0
        self.doc_freq: Counter = Counter()
        self.num_docs = 0
        self._built = False

    def index_documents(self, docs: List[str], metadatas: List[Dict]):
        self.docs = docs
        self.metadatas = metadatas
        self.num_docs = len(docs)
        total_len = 0
        for doc in docs:
            tokens = self._tokenize(doc)
            total_len += len(tokens)
            for token in set(tokens):
                self.doc_freq[token] += 1
        self.avg_doc_len = total_len / self.num_docs if self.num_docs > 0 else 1.0
        self._built = True

    def search(self, query: str, k: int = 5) -> List[Tuple[str, Dict, float]]:
        if not self._built or self.num_docs == 0:
            return []
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []
        scored = []
        for i, doc in enumerate(self.docs):
            score = self._bm25_score(query_tokens, doc)
            if score > 0:
                scored.append((score, i))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [(self.docs[idx], self.metadatas[idx], score) for score, idx in scored[:k]]

    def _tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        text = text.lower()
        words = re.findall(r'[a-z]+', text)
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        return words + chinese_chars

    def _bm25_score(self, query_tokens: List[str], doc: str) -> float:
        doc_tokens = self._tokenize(doc)
        doc_len = len(doc_tokens)
        doc_counter = Counter(doc_tokens)
        score = 0.0
        for token in set(query_tokens):
            tf = doc_counter.get(token, 0)
            if tf == 0:
                continue
            df = self.doc_freq.get(token, 0)
            if df == 0:
                continue
            idf = math.log((self.num_docs - df + 0.5) / (df + 0.5) + 1.0)
            numerator = tf * (self.k1 + 1.0)
            denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_len))
            score += idf * (numerator / denominator)
        return score


# =====================================================================
#  知识库管理器（RAG 核心）
# =====================================================================

class RAGKnowledgeBase:
    """RAG 知识库管理器，整合文档检索 + 商品检索"""

    def __init__(self):
        self.retriever = BM25()
        self.chunks: List[str] = []
        self.metadatas: List[Dict] = []
        self._load_state()
        self._load_products_into_bm25()

    def add_document(self, file_path: str) -> int:
        text = load_document(file_path)
        source_name = os.path.basename(file_path)
        chunks = split_text(text)
        added = 0
        for chunk in chunks:
            if not chunk.strip():
                continue
            self.chunks.append(chunk)
            self.metadatas.append({
                "source": source_name, "type": "document",
                "chunk_index": len(self.chunks) - 1,
                "added_at": datetime.now().isoformat(),
            })
            added += 1
        if added > 0:
            self._rebuild_index()
            self._save_state()
        return added

    def add_text(self, text: str, source: str = "直接输入") -> int:
        chunks = split_text(text)
        added = 0
        for chunk in chunks:
            if not chunk.strip():
                continue
            self.chunks.append(chunk)
            self.metadatas.append({
                "source": source, "type": "text",
                "chunk_index": len(self.chunks) - 1,
                "added_at": datetime.now().isoformat(),
            })
            added += 1
        if added > 0:
            self._rebuild_index()
            self._save_state()
        return added

    def search(self, query: str, k: int = 5) -> List[Tuple[str, Dict, float]]:
        """BM25 检索文档知识库"""
        results = self.retriever.search(query, k)
        # 同时返回商品搜索结果作为补充
        if not results:
            products = self._search_products(query, k=3)
            for p in products:
                results.append((
                    f"[商品] {p['name']}\n分类：{p.get('category','')}\n"
                    f"价格：￥{p.get('price',0)}\n品牌：{p.get('brand','')}\n"
                    f"简介：{p.get('desc','')}",
                    {"source": f"product:{p.get('id','')}", "type": "product"},
                    0.5
                ))
        return results[:k]

    def get_stats(self) -> int:
        return len(self.chunks)

    def clear(self):
        self.chunks = []
        self.metadatas = []
        self.retriever = BM25()
        self._save_state()

    def _load_products_into_bm25(self):
        try:
            if os.path.exists(PRODUCTS_FILE):
                with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
                    products = json.load(f)
                for i, p in enumerate(products):
                    name = p.get("name", "")
                    desc = p.get("desc", "")
                    category = p.get("category", "")
                    tags = " ".join(p.get("tags", []))
                    brand = p.get("brand", "")
                    price = p.get("price", 0)
                    content = (
                        f"[商品] {name}\n分类：{category}\n"
                        f"价格：￥{price}\n简介：{desc}\n"
                        f"标签：{tags}\n品牌：{brand}"
                    )
                    self.chunks.append(content)
                    self.metadatas.append({
                        "source": f"product:{p.get('id', f'p{i}')}",
                        "type": "product",
                        "product_name": name,
                    })
                if products:
                    self._rebuild_index()
        except Exception:
            pass

    def _search_products(self, query: str, k: int = 3) -> List[Dict]:
        try:
            if os.path.exists(PRODUCTS_FILE):
                with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
                    products = json.load(f)
                query_lower = query.lower()
                scored = []
                for p in products:
                    score = 0
                    if query_lower in p.get("name", "").lower():
                        score += 10
                    if query_lower in p.get("desc", "").lower():
                        score += 5
                    tags = p.get("tags", [])
                    if any(query_lower in t.lower() for t in tags):
                        score += 8
                    if score > 0:
                        scored.append((score, p))
                scored.sort(key=lambda x: x[0], reverse=True)
                return [p for _, p in scored[:k]]
        except Exception:
            pass
        return []

    def _rebuild_index(self):
        self.retriever = BM25()
        self.retriever.index_documents(self.chunks, self.metadatas)

    def _save_state(self):
        try:
            state = {"chunks": self.chunks, "metadatas": self.metadatas}
            os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False)
        except Exception:
            pass

    def _load_state(self):
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    state = json.load(f)
                self.chunks = state.get("chunks", [])
                self.metadatas = state.get("metadatas", [])
                if self.chunks:
                    self.retriever.index_documents(self.chunks, self.metadatas)
        except Exception:
            self.chunks = []
            self.metadatas = []


# =====================================================================
#  全局实例
# =====================================================================

_kb = None


def get_kb() -> RAGKnowledgeBase:
    global _kb
    if _kb is None:
        _kb = RAGKnowledgeBase()
    return _kb


def search_documents(query: str, k: int = 4) -> List[Tuple]:
    from types import SimpleNamespace
    results = get_kb().search(query, k)
    docs = []
    for content, meta, score in results:
        doc = SimpleNamespace()
        doc.page_content = content
        doc.metadata = meta
        docs.append((doc, score))
    return docs


def add_document_to_db(file_path: str) -> int:
    return get_kb().add_document(file_path)


def add_document_text_to_db(text: str) -> int:
    return get_kb().add_text(text)
