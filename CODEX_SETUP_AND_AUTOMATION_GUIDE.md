# Aethelgard + Codex: Parça Parça Otomatik İnşa Akışı

## Güvenli kurgu

Aethelgard için en sağlıklı otomasyon, Codex'in tek oturumda sonu belirsiz biçimde her şeyi
değiştirmesi değildir. Her görevde yalnızca bir doğrulanabilir mimari dilim yapılır:

1. Codex güncel `dev` dalını okur.
2. `AGENTS.md`, `REPORT.md`, `VERSION.md`, `CHANGELOG.md` içinden sıradaki eksik küçük fazı seçer.
3. Yalnız o fazı kodlar ve test eder.
4. Belgelendirmeyi günceller.
5. Tek PR açar ve durur.
6. İnceleme/merge sonrasında aynı görev tekrar çalıştırılır; yeni `dev` durumundan sıradaki fazı seçer.

Bu yöntem projenin parçalarını lego gibi birleştirir, ancak her blok laboratuvar etiketiyle gelir:
ne ölçüldü, ne modellendi, ne hâlâ bilinmiyor.

## Kurulum

1. Codex Cloud içinde GitHub hesabını bağla ve `werim/Aethelgard-` deposu için ortam oluştur.
2. Çalışma tabanı olarak `dev` dalını seç.
3. İlk değişiklik olarak depo köküne bu paketteki `AGENTS.md` dosyasını eklet veya kendin commit et.
4. Codex ortamında Python bağımlılıklarının kurulabildiğini ve proje kontrol komutlarının
   çalıştırılabildiğini doğrula.
5. Codex/GitHub ayarlarında otomatik PR review kullanılabilir; ancak bu proje için otomatik merge
   açma. Risk sınırlarını ve PAPER-only emniyetini insan incelemesi korumalıdır.
6. Her yeni uygulama turunda `CODEX_RUN_NEXT_INCREMENT.txt` içeriğini görev olarak gönder.

## Neden AGENTS.md?

Codex, repository içindeki `AGENTS.md` talimatlarını iş yapmadan önce okur. Bu, her yeni görevde
PAPER-only güvenliği, test zorunluluğu, belge güncellemesi ve tek-faz sınırının tekrar taşınmasını
sağlar.

## Güncel başlangıç noktası

Bu paket hazırlanırken `dev` dalından okunan dokümanlar şunu kaydediyordu:

- Sürüm: `0.2.0`
- Tamamlanan sınır: Phase 2, verilen tarihsel kline satırları için doğrulama/provenance/hash sınırı
- Operasyonel sınıflandırma: `RESEARCH_ONLY`
- Sıradaki tavsiye edilen artım: salt-okunur Binance Futures tarihsel kline edinimi; deterministik
  sayfalama, retry/rate-limit davranışı, stale-data reddi, request/provenance tutarlılığı ve
  değiştirilemez yerel artifact + metadata/checksum kalıcılığı

Görev promptu bu bilgiyi yalnızca başlangıç ipucu kabul eder; her çalışmada depoyu yeniden
okumadan faz seçmez.

## Kullanım kuralı

Codex bir PR açtıktan sonra aynı görev içinde sonraki fazı başlatma. PR test ve incelemeden
geçip `dev` dalına alındıktan sonra aynı launcher promptunu tekrar gönder. Böylece her PR tek
mühendislik iddiasını taşır ve hata olduğunda hangi tuğlanın çatladığı görülebilir.
