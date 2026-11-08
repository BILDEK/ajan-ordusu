# Ajan Ordusu — sınırlı bulut araştırması

Bu repo bağımsız Python yazılım/veri testleri çalıştırır. PC uzaktan kumandası, sürekli sunucu veya sınırsız AI ajanı değildir; trading hesabına erişmez, emir vermez, secret kullanmaz.

- `ajan.yml`: altı saatte bir BTC/ETH/SOL public OKX funding/OI özeti.
- `arge.yml`: ayrı `kernel/` araştırma alanı; UTC 00:17/06:17/12:17/18:17, manuel ve ilgili kaynak push'u (`main`); PR yok. UTC gününe göre sayısal integrasyon yakınsama testi veya mevcut ETH 5m araştırması dönüşümlü çalışır. Ledger rezervasyonu başarılı biçimde repo'ya yazılmadan araştırma başlamaz. Gate2dk, tek araştırma runner'ı8dk, ayrı küçük bulgu yayını2dk; PC/bot değişmez. Ayrıntılı kurallar: [KERNEL.md](KERNEL.md).
- `arge_ci.py`: 2000 teyitli mum; ilk %70 eğitim, son %30 holdout. Volatilite eşiği ve aday seçimi yalnız eğitimden. Aday içinde eşzamanlı pozisyon yok. Yaklaşık maliyet varsayımı: toplam 12 bps (10 ücret + 2 kayma), kullanıcı hesap ücreti değildir. Eğitimde en az20 örnek; holdout küçükse sonuç güvenilmez.
- Sonuçlar workflow **Summary** ve logda; değişen küçük bulgular `kernel/FINDINGS.md` / `kernel/findings.json` dosyalarına ayrı write job ile yazılır. Artifact/cache yüklenmez. Bu günlük araştırma hafızasıdır; model ağırlığı öğrenmesi, garantili gelir veya net portföy getirisi değildir. Funding, gap fill ve piyasa etkisi eksiktir; kod/veri ürünü fikirlerinin talebi doğrulanmış değildir.
- `strateji_backtest.py` sadece anahtarsız public veri kullanan motor kopyası; yerel cache/kişisel dosyalar taşınmadı. Orijinal motorun eski tam örneklem rejim sıralaması canlı işlem kanıtı değildir.

## Ücretsiz kapasite (2026-11-09)

Public standart `ubuntu-latest`: iş başına **4 vCPU / 16GB RAM / 14GB SSD**, standart GPU yok. GitHub Free: hesap genelinde **20 eşzamanlı iş** sınırı; teorik **80 vCPU / 320GB toplam RAM**, ama 20 ayrı geçici VM. Kaynaklar tek bilgisayar gibi birleşmez, rezerve değildir, kuyruk/başlangıç zamanı garanti edilmez. Tek standart job en fazla6 saat; bizim araştırma job'ı8 dakika ile sınırlı.

Kalıcı fail-closed `kernel/budget.json`: çalışma ÖNCESİ10dk rezervasyon, günde en çok4 çalışma/40 rezervasyon-dk, UTC ayında en çok1200 rezervasyon-dk (31günlük ayda son4 çalışma yapılmaz). Son12 ay/40 gün tutulur, iptal/hata rezervasyonu iade edilmez. Bunlar resmî public dakika kotası değil kendi araştırma sınırımızdır; gate, provisioning, bulgu yayını ve mevcut analiz ek süreleri dâhil toplam platform faturalaması için garanti değildir. Veri/test geçmezse sonuç üretilmez; süre gerçek iş yüküne bağlıdır.

Public standart runner compute ücretsizdir; ücretli büyük/GPU runner, paid API, ek hesap ve depolama satın alma yok. Free artifact depolama500MB, cache varsayılan10GB/repo; bu workflow ikisini de doldurmaz. 60 günlük repo hareketsizliğinde zamanlama kapanabilir. GitHub Actions kalıcı hosting veya genel amaçlı sınırsız compute çiftliği olarak kullanılmaz.

Resmî kaynaklar:
- https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- https://docs.github.com/en/actions/reference/limits
