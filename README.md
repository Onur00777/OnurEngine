# OnurEngine (BetaOne)

Kendi eğittiğim derin öğrenme modeli ile klasik satranç değerlendirmesini birleştiren hibrit bir satranç motoru. Matematiksel hamle hesabı ile yapay zeka ağı birlikte kullanılmıştır.

BetaOne modeli **Google Colab** üzerinde eğitildi (yaklaşık 1000 oyunluk veri ile), ardından ağırlıklar (`betaone.pt`) bu repoya aktarıldı. Motor tahtayı CNN ile puanlar; minimax aramasıyla en iyi hamleyi seçer. Üzerinde oynayabileceğin arayüzler de projede hazır.

## Özellikler

- **Hibrit değerlendirme:** PyTorch modeli (`betaone.pt`) + klasik taş değerleri
- **Arama:** Minimax tabanlı hamle seçimi
- **API:** FastAPI ile `POST /get_move` (FEN → UCI hamle)
- **Arayüzler:**
  - Flask + chessboard.js (`app.py`)
  - Next.js + `react-chessboard` (`satranc-arayuzu/`)

## Proje yapısı

```
OnurEngine/
├── main.py              # Motor, model ve arama mantığı
├── api.py               # FastAPI backend
├── app.py               # Flask masaüstü/web arayüzü
├── gui.py / gui_ai.py   # Ek GUI denemeleri
├── betaone.pt           # Ana model ağırlıkları
├── betaone_alphago.pt   # Alternatif model
├── betaone_eski.pt      # Eski model yedeği
└── satranc-arayuzu/     # Next.js satranç arayüzü
```

## Gereksinimler

**Python**

- Python 3.10+
- `chess`, `torch`, `numpy`, `fastapi`, `uvicorn`, `flask`, `pydantic`

Örnek kurulum:

```bash
pip install -r requirements.txt
```

**Next.js arayüz**

- Node.js 18+

```bash
cd satranc-arayuzu
npm install
```

## Çalıştırma

### 1) Motor API (FastAPI)

Proje kökünden:

```bash
uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

Örnek istek:

```bash
curl -X POST http://127.0.0.1:8000/get_move ^
  -H "Content-Type: application/json" ^
  -d "{\"fen\": \"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1\"}"
```

### 2) Flask arayüzü

```bash
python app.py
```

### 3) Next.js arayüzü

API’nin `8000` portunda açık olduğundan emin ol, sonra:

```bash
cd satranc-arayuzu
npm run dev
```

Tarayıcı: [http://localhost:3000](http://localhost:3000)

Sen beyazlarla oynarsın; siyah hamleleri motor üretir.

## Model notu

- Eğitim ortamı: **Google Colab**
- Ağırlık dosyası: kökteki `betaone.pt` (Colab’den indirilip projeye konur)
- Motor bu dosyayı yükler; yoksa çalışır ama değerlendirme rastgele/zayıf olur
- `betaone_alphago.pt` ve `betaone_eski.pt` alternatif / yedek ağırlıklardır

## Geliştirme fikirleri

- Arama derinliğini ayarlanabilir yapmak
- Açılış kitabı eklemek
- Model eğitim pipeline’ını repoya belgelemek
- CORS’u production için sıkılaştırmak

## Lisans

Şimdilik özel proje. İleride lisans eklenebilir.
