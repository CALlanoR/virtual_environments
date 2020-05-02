from celery.utils.log import get_task_logger

from setup import app

logger = get_task_logger(__name__)

@app.task(bind=True, name='save_publication', queue='new_publications')
def save_publication(self, publication):
   logger.info(f'Build articles: {url}')