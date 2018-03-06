from django.db import models

# Create your models here.


class CEScodes(models.Model):
    ces_code = models.IntegerField(primary_key=True)
    ces_description = models.CharField(max_length=100)

    def __str__(self):
        return "%s" % self.ces_description


class ClientRaw(models.Model):
    uw_client_id = models.IntegerField()
    assessment_date = models.DateTimeField()
    assessing_organization = models.CharField(max_length=300)
    assessment_score = models.IntegerField()
    ce_status = models.ForeignKey(CEScodes, db_constraint=False, null=True, blank=True, on_delete=models.DO_NOTHING)
    individual_or_family = models.CharField(max_length=10)

    def __str__(self):
        return "%s" % self.uw_client_id


class Client(models.Model):
    uw_client_id = models.IntegerField()
    assessment_date = models.DateTimeField()
    assessing_organization = models.CharField(max_length=300)
    assessment_score = models.IntegerField()
    ce_status = models.ForeignKey(CEScodes, db_constraint=False, null=True, blank=True, on_delete=models.DO_NOTHING)
    individual_or_family = models.CharField(max_length=10)

    def __str__(self):
        return "%s" % self.uw_client_id


class SheetUpload(models.Model):
    upload_date = models.DateTimeField(auto_now_add=True)
    vispdat_file = models.FileField()
    fvispdat_file = models.FileField()
    psh_file = models.FileField()
    rrh_file = models.FileField()


class Home(models.Model):
    uw_client_id = models.IntegerField()
    ces_code = models.IntegerField(null=True, default=None)
    source = models.CharField(max_length=10)
