from django.core.exceptions import ValidationError
from django.db import models
import uuid

# Parameters
MAX_CORPUS_SIZE = 1000  # maximum collection size allowed

# ----------------------------------------

# Corpus size validator
def validate_corpus_size(value):
    if value < 1:
        raise ValidationError('Collection must not be empty')
    elif value > MAX_CORPUS_SIZE:
        raise ValidationError('Collection is too large')

# ----------------------------------------

# Documents Collection model
class Collection(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=300, blank=True)
    corpus_size = models.IntegerField(validators=[validate_corpus_size])
