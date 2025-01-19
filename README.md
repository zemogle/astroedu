# astroEDU Internationalization version

While this is in progress these are the install Instructions

- If there is a *weird* error when running porting script run:
```
docker-compose run web python manage.py fixtree
```
- don't forget to include the images
- Find out why pages which have italian versions are ignored.


## Starting a new language edition

### Set up language files

- Add the language to `LANGUAGES` setting in `base.py`.
- Run:
```
docker compose web run python manage.py makemessages -l <newlanguagecode>
```

Translate the `.po` files generated, then compile them with:

```
docker compose web run python manage.py compilemessages
```

### Set up wagtail-localise

- Add the language in Wagtail settings via `settings > Locales > + Add Locale`
- The language you enabled will appear in the as a new language
- **Important** Do not enable "Synchoronise content from another locale" . This would copy all the english versions of all content into the new language edition.
- Begin translating pages