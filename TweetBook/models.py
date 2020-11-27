from django.db import models
from django.urls import reverse

# Create your models here
class Tweets(models.Model):
        """Modello che definisce ogni singolo utente che ha creato almeno un tweet analizzato"""

        # Fields
        id_tweet = models.IntegerField(primary_key=True)
        username = models.CharField(max_length=15, help_text='Who sent the content?')
        tweet_content = models.CharField(max_length=280, help_text='Tweet Content')
        tweet_location = models.CharField(max_length=20, help_text='Location of  the tweet')

        # Metadata
        ordering = [username]

        #Methods
        def __str__(self):
        	return self.username
        def get_absolute_url(self):
        	return reverse('tweet-detail-view', args=[str(self.id)])
