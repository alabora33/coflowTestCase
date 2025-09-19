{
    "name": "Field Service Visit",
    "version": "17.0.1.0.0",
    "summary": "Visit planner + FastAPI stock sync demo",
    "depends": ["base", "stock", "product", "hr", "mail"],
    "data": [
        "security/field_service_security.xml",
        "security/field_service_model_access.xml",
        "security/ir.model.access.csv",
    "views/field_service_views.xml",
    "views/menus.xml",
        "views/stock_sync_wizard_views.xml",
        "data/field_service_mail_template.xml",
        "data/field_service_scheduled_action.xml",
    ],
    "installable": True,
    "application": False,
}
