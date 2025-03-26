# Django REST API - Kullanıcı ve Profil Yönetim Sistemi

Bu proje, rol tabanlı yetkilendirme, kullanıcı tipleri ve profil yönetimi özelliklerini içeren kapsamlı bir Django REST API uygulamasıdır.

## Özellikler

- **Kullanıcı Kimlik Doğrulama**
  - Giriş ve Kayıt işlemleri
  - Token tabanlı kimlik doğrulama
  - Güvenli şifre yönetimi

- **Profil Yönetimi**
  - Özel kullanıcı profilleri
  - Profil fotoğrafı yükleme
  - Telefon numarası yönetimi
  - Kullanıcı tipleri ve rolleri

- **Rol Tabanlı Yetkilendirme**
  - Esnek kullanıcı rolleri
  - Özel kullanıcı tipleri
  - İzin yönetimi

- **API Özellikleri**
  - RESTful endpoints
  - Swagger dokümantasyonu
  - Sayfalama desteği
  - Dosya yükleme işlemleri

## API Endpointleri

### Kimlik Doğrulama
- `POST /api/login/` - Kullanıcı girişi
- `POST /api/register/` - Kullanıcı kaydı

### Profil Yönetimi
- `GET /api/profiles/` - Tüm profilleri listele
- `GET /api/profiles/<id>/` - Belirli bir profili getir
- `PUT /api/profiles/<id>/` - Profil güncelle
- `DELETE /api/profiles/<id>/` - Profil sil

### Kullanıcı Tipleri
- `GET /api/user-types/` - Tüm kullanıcı tiplerini listele
- `POST /api/user-types/` - Kullanıcı tipi oluştur
- `GET /api/user-types/<id>/` - Belirli bir kullanıcı tipini getir
- `PUT /api/user-types/<id>/` - Kullanıcı tipini güncelle
- `DELETE /api/user-types/<id>/` - Kullanıcı tipini sil

### Kullanıcı Rolleri
- `GET /api/user-roles/` - Tüm kullanıcı rollerini listele
- `POST /api/user-roles/` - Kullanıcı rolü oluştur
- `GET /api/user-roles/<id>/` - Belirli bir kullanıcı rolünü getir
- `PUT /api/user-roles/<id>/` - Kullanıcı rolünü güncelle
- `DELETE /api/user-roles/<id>/` - Kullanıcı rolünü sil

## Teknoloji Altyapısı

- **Backend:** Django 5.0.3
- **API Framework:** Django REST Framework
- **Veritabanı:** SQLite (varsayılan)
- **Kimlik Doğrulama:** Token tabanlı
- **Dokümantasyon:** drf-yasg (Swagger)
- **Dosya İşleme:** Pillow

## Kurulum

1. Projeyi klonlayın:
```bash
git clone https://github.com/kullaniciadi/LearninWithDjangoRest.git
cd LearninWithDjangoRest
```

2. Sanal ortam oluşturun ve aktif edin:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac için
# veya
venv\Scripts\activate  # Windows için
```

3. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

4. Veritabanı migrasyonlarını yapın:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Süper kullanıcı oluşturun (isteğe bağlı):
```bash
python manage.py createsuperuser
```

6. Geliştirme sunucusunu başlatın:
```bash
python manage.py runserver
```

## Varsayılan Kullanıcılar

### Admin Kullanıcısı
- Kullanıcı Adı: admin
- Şifre: Admin1234admin.

### Test Kullanıcıları
- Kullanıcı Adları: test01, test02, test03
- Şifre: Test1234test.

## API Dokümantasyonu

Sunucu çalışır durumdayken, API dokümantasyonuna şu adreslerden erişebilirsiniz:
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

## Proje Yapısı

```
LearninWithDjangoRest/
├── api/                    # Ana API uygulaması
│   ├── migrations/        # Veritabanı migrasyonları
│   ├── models.py         # Veri modelleri
│   ├── serializers.py    # API serileştiricileri
│   ├── views.py         # API görünümleri
│   └── urls.py          # API yönlendirmeleri
├── LearninWithDjangoRest/ # Proje ayarları
├── media/                # Kullanıcı yükleme dosyaları
├── manage.py            # Django yönetim scripti
└── requirements.txt     # Proje bağımlılıkları
```

## Modeller

### UserType (Kullanıcı Tipi)
- name: CharField (İsim)
- description: TextField (Açıklama)
- timestamps: created_at, updated_at (Oluşturma ve güncelleme zamanları)

### UserRole (Kullanıcı Rolü)
- name: CharField (İsim)
- description: TextField (Açıklama)
- timestamps: created_at, updated_at (Oluşturma ve güncelleme zamanları)

### Profile (Profil)
- user: OneToOneField -> User (Kullanıcı)
- phone_number: CharField (Telefon numarası)
- profile_picture: ImageField (Profil fotoğrafı)
- user_type: ForeignKey -> UserType (Kullanıcı tipi)
- user_roles: ManyToManyField -> UserRole (Kullanıcı rolleri)
- timestamps: created_at, updated_at (Oluşturma ve güncelleme zamanları)

## Katkıda Bulunma

1. Projeyi fork edin
2. Özellik dalınızı oluşturun (`git checkout -b özellik/harika-özellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Harika bir özellik eklendi'`)
4. Dalınıza push yapın (`git push origin özellik/harika-özellik`)
5. Bir Pull Request oluşturun

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır - detaylar için LICENSE dosyasına bakınız.

## Destek

Destek için lütfen GitHub deposunda bir issue açın veya geliştirme ekibiyle iletişime geçin.