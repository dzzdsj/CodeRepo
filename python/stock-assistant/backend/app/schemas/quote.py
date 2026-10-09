"""行情相关 Pydantic 模型。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Quote(BaseModel):
    """单只股票实时行情。"""

    code: str
    name: str
    price: float
    changePct: float = Field(description="涨跌幅 %")
    changeAmt: float = Field(description="涨跌额")
    volume: float = Field(description="成交量（手）")
    amount: float = Field(description="成交额（元）")
    high: float
    low: float
    open: float
    preClose: float
    timestamp: int = Field(description="行情时间戳 ms")
    speed5m: float | None = Field(default=None, description="5分钟涨速 %")
    volRatio: float | None = Field(default=None, description="量比")


class IndexQuote(BaseModel):
    """大盘指数实时行情。"""

    code: str
    name: str
    price: float
    changePct: float
    changeAmt: float
    timestamp: int


class FundFlowItem(BaseModel):
    """单日资金流向数据。"""

    date: str = Field(description="日期 YYYY-MM-DD")
    close: float = Field(description="收盘价")
    changePct: float = Field(description="涨跌幅 %")
    mainNetInflow: float = Field(description="主力净流入净额（元）")
    mainNetInflowRatio: float = Field(description="主力净流入净占比 %")
    superLargeNetInflow: float = Field(description="超大单净流入净额（元）")
    superLargeNetInflowRatio: float = Field(description="超大单净流入净占比 %")
    largeNetInflow: float = Field(description="大单净流入净额（元）")
    largeNetInflowRatio: float = Field(description="大单净流入净占比 %")
    mediumNetInflow: float = Field(description="中单净流入净额（元）")
    mediumNetInflowRatio: float = Field(description="中单净流入净占比 %")
    smallNetInflow: float = Field(description="小单净流入净额（元）")
    smallNetInflowRatio: float = Field(description="小单净流入净占比 %")


class FundFlowResponse(BaseModel):
    """资金流向响应。"""

    code: str
    name: str
    latest: FundFlowItem | None = Field(description="最新一日资金流向")
    history: list[FundFlowItem] = Field(description="历史资金流向列表")
