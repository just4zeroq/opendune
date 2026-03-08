"""
告警API路由
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from src.common.models import Alert, AlertRule
from src.data_service.services.alert_service import AlertService

router = APIRouter()
alert_service = AlertService()


@router.get("/rules")
async def get_alert_rules(
    is_active: Optional[bool] = None,
    rule_type: Optional[str] = None,
):
    """获取告警规则列表"""
    try:
        return await alert_service.get_rules(
            is_active=is_active,
            rule_type=rule_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rules")
async def create_alert_rule(rule: AlertRule):
    """创建告警规则"""
    try:
        return await alert_service.create_rule(rule)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules/{rule_id}")
async def get_alert_rule(rule_id: int):
    """获取告警规则详情"""
    try:
        rule = await alert_service.get_rule(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        return rule
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/rules/{rule_id}")
async def update_alert_rule(rule_id: int, rule: AlertRule):
    """更新告警规则"""
    try:
        return await alert_service.update_rule(rule_id, rule)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/rules/{rule_id}")
async def delete_alert_rule(rule_id: int):
    """删除告警规则"""
    try:
        await alert_service.delete_rule(rule_id)
        return {"message": "Rule deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_alert_history(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """获取告警历史"""
    try:
        return await alert_service.get_alerts(
            status=status,
            severity=severity,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/history/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int):
    """确认告警"""
    try:
        await alert_service.acknowledge_alert(alert_id)
        return {"message": "Alert acknowledged"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/history/{alert_id}/resolve")
async def resolve_alert(alert_id: int):
    """解决告警"""
    try:
        await alert_service.resolve_alert(alert_id)
        return {"message": "Alert resolved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
