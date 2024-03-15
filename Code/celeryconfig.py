from datetime import timedelta

beat_schedule = {
	'send-cart-reminder': {
		'task': 'webhooks.send_cart_reminder',
		'schedule': timedelta(days=1, hours=17),
	},
	'send-monthly-activity-report': {
		'task': 'webhooks.send_monthly_report',
		'schedule': timedelta(days=1),
	},
}