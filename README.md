# Ajan Ordusu — sınırlı bulut araştırması

Bu repo bağımsız Python yazılım/veri testleri çalıştırır. PC uzaktan kumandası, sürekli sunucu veya sınırsız AI ajanı değildir; trading hesabına erişmez, emir vermez, secret kullanmaz.

- `ajan.yml`: altı saatte bir BTC/ETH/SOL public OKX funding/OI özeti.
- `arge.yml`: altı saatte bir (UTC 00:17/06:17/12:17/18:17, zamanlama gecikebilir) TEK ETH 5m araştırma/regresyon testi. Manuel ve ilgili kod push'u ile de çalışır. Tek makine; en fazla 10 dakika; sonrasında runner kapanır. PC üzerinde işlem yapmaz.
- `arge_ci.py`: 2000 teyitli mum; ilk %70 eğitim, son %30 holdout. Volatilite eşiği ve aday seçimi yalnız eğitimden. Aday içinde eşzamanlı pozisyon yok. Yaklaşık maliyet varsayımı: toplam 12 bps (10 ücret + 2 kayma), kullanıcı hesap ücreti değildir. Eğitimde en az20 örnek; holdout küçükse sonuç güvenilmez.
- Sonuçlar workflow **Summary** ve logda, süre/örneklem/uyarılarıyla tutulur. Artifact/cache yüklenmez; küçük bulgular incelenip kalıcı nota geçirilir. Sonuç bir model öğrenmesi veya net portföy getirisi değildir; funding, gap fill ve piyasa etkisi eksiktir.
- `strateji_backtest.py` sadece anahtarsız public veri kullanan motor kopyası; yerel cache/kişisel dosyalar taşınmadı. Orijinal motorun eski tam örneklem rejim sıralaması canlı işlem kanıtı değildir.

## Ücretsiz kapasite (2026-11-09)

Public standart `ubuntu-latest`: iş başına **4 vCPU / 16GB RAM / 14GB SSD**, standart GPU yok. GitHub Free: hesap genelinde **20 eşzamanlı iş** sınırı; teorik **80 vCPU / 320GB toplam RAM**, ama 20 ayrı geçici VM. Kaynaklar tek bilgisayar gibi birleşmez, rezerve değildir, kuyruk/başlangıç zamanı garanti edilmez. Tek standart job en fazla6 saat; bizim test10 dakika ile sınırlı.

Başlangıç planı: günde4 × en çok10dk = en çok40 runner-dakika/gün; 4 vCPU üzerinden teorik160 vCPU-dakika (=2.67 vCPU-saat) tahsis zarfı. Bu tüketilecek hedef değil üst sınırdır; script tek iş parçacıklı, süre ağ ve gerçek veriye bağlıdır. RAM16GB tek aktif işin tavanı, sürekli ayrılmış değildir. Gerçek süre summary'de ölçülür.

Public standart runner compute ücretsizdir; ücretli büyük/GPU runner, paid API, ek hesap ve depolama satın alma yok. Free artifact depolama500MB, cache varsayılan10GB/repo; bu workflow ikisini de doldurmaz. 60 günlük repo hareketsizliğinde zamanlama kapanabilir. GitHub Actions kalıcı hosting veya genel amaçlı sınırsız compute çiftliği olarak kullanılmaz.

Resmî kaynaklar:
- https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- https://docs.github.com/en/actions/reference/limits
