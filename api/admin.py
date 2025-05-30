from django import forms
from django.contrib import admin

from .models import Proxy, User, UserAgent, hash_url


class ProxyAdminForm(forms.ModelForm):
    class Meta:
        model = Proxy
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        url = cleaned_data.get("url")
        if tmp := Proxy.objects.filter(url=url).exists():
            exists = tmp
        else:
            url_hash = hash_url(url)
            if self.instance.pk:
                exists = (
                    Proxy.objects.exclude(pk=self.instance.pk)
                    .filter(url_hash=url_hash)
                    .exists()
                )
            else:
                exists = Proxy.objects.filter(url_hash=url_hash).exists()

        if exists:
            self.add_error("url", "Прокси с таким URL уже существует.")

        return cleaned_data


class ProxyAdmin(admin.ModelAdmin):
    form = ProxyAdminForm


admin.site.register(Proxy, ProxyAdmin)
admin.site.register([User, UserAgent])
