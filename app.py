import math
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Nota da Lu • Comparador de Notebooks", page_icon="💻", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1500px}
[data-testid="stMetric"] {background: #f7f8fb; border: 1px solid #e7e9ef; padding: 14px; border-radius: 14px}
h1,h2,h3 {letter-spacing: -.02em}
.small {font-size:.88rem;color:#68707d}
.badge {display:inline-block;padding:.22rem .55rem;border-radius:999px;background:#eef2ff;margin-right:.3rem;font-size:.78rem}
</style>
""", unsafe_allow_html=True)

NOTEBOOKS = [
{
"Marca":"Samsung","Modelo / configuração":"Galaxy Book4 15,6” — i5-1335U / 8GB / 512GB","Código / SKU":"NP750XGJ-KG3BR","Ano/geração aproximada":"2024 / Intel 13ª","Sistema operacional":"Windows 11 Home","CPU":"Intel Core i5-1335U","Família / geração CPU":"13ª geração (Raptor Lake-U)","Arquitetura CPU":"Híbrida","Núcleos":10,"P-cores":2,"E-cores":8,"LP E-cores":0,"Threads":12,"Clock base / referência (GHz)":1.3,"Turbo máx. (GHz)":4.6,"Cache L3 (MB)":12,"NPU":"Não","GPU integrada":"Intel Iris Xe Graphics","GPU dedicada":"Não","RAM instalada (GB)":8,"Tipo RAM":"LPDDR4x","Velocidade RAM":"N/D","Configuração RAM":"8GB onboard","RAM soldada":"Sim","Slots RAM físicos":0,"Slots RAM livres":0,"RAM máxima oficial (GB)":8,"Dual-channel de fábrica":"Sim (LPDDR)","Expansão de RAM":"Não","SSD instalado (GB)":512,"Tipo/interface SSD":"NVMe","Formato SSD":"M.2","Slots M.2 totais":2,"Slots M.2 livres":1,"Armazenamento máx./observação":"SSD expansível; 2 slots M.2 no chassi","Tela (pol.)":15.6,"Resolução":"1920×1080","Proporção":"16:9","Painel":"IPS / LED","Acabamento":"Antirreflexo","Touch":"Não","Taxa de atualização (Hz)":60,"Brilho (nits)":"N/D","Cobertura de cores":"N/D","Contraste":"N/D","Webcam":"HD 720p / 1 MP","Tampa de privacidade":"N/D","Teclado ABNT2":"Sim","Teclado numérico":"Sim","Teclado retroiluminado":"Não informado","Touchpad":"Clickpad","Wi‑Fi":"Wi‑Fi 6 (802.11ax) 2×2","Bluetooth":"5.2","Ethernet RJ‑45":"Sim, Gigabit","USB‑A":"2× USB 3.2","USB‑C":"2× USB‑C","Thunderbolt / USB4":"Não informado","USB‑C com vídeo":"Sim (família)","USB‑C com carregamento":"Sim","HDMI":"1× HDMI (família Book4; versão 2.1 em ficha BR)","Leitor de cartões":"microSD","Áudio P2":"1× combo 3,5 mm","Áudio / alto-falantes":"Estéreo 2×2W, Dolby Atmos","Microfones":"Dual array","Bateria (Wh)":54,"Células":"N/D","Autonomia declarada":"N/D","Carregador (W)":45,"Carregamento USB‑C":"Sim","Largura (mm)":356.6,"Profundidade (mm)":229.1,"Espessura (mm)":15.4,"Peso (kg)":1.55,"Material / construção":"Corpo metálico","Cor":"Grafite","TPM":"Sim","Trava de segurança":"Sim","Leitor biométrico":"Não informado","Garantia informada":"12 meses (mercado BR, confirmar anúncio)","Destaques objetivos":"Leve; bateria 54Wh; RJ‑45; 2 USB‑C; segundo slot SSD","Limitações / ressalvas":"RAM de 8GB soldada e sem expansão; brilho/gamut não publicados na ficha deste SKU","Link do anúncio":"https://www.mercadolivre.com.br/notebook-samsung-galaxy-book4-intel-core-i5-1335u-13-ghz-ate-46ghz-12-mb-l3-cache-windows-11-home-8gb-512gb-ssd-iris-xe-156-full-hd-led-155kg/p/MLB37044038","Fonte técnica principal":"https://www.samsung.com/br/computers/samsung-book/galaxy-book4-15-6-inch-i5-8gb-512gb-np750xgj-kg3br/","Fonte complementar":"https://news.samsung.com/br/samsung-lanca-novo-galaxy-book4-no-brasil"
},
{
"Marca":"Acer","Modelo / configuração":"Aspire 16 A16-71M-55H0 — Ultra 5 115U / 16GB / 512GB","Código / SKU":"NX.JQLAL.001","Ano/geração aproximada":"2025 / Core Ultra Série 1","Sistema operacional":"Windows 11 Home 64-bit","CPU":"Intel Core Ultra 5 115U","Família / geração CPU":"Core Ultra Série 1 (Meteor Lake-U)","Arquitetura CPU":"Híbrida + LP E-core","Núcleos":8,"P-cores":2,"E-cores":4,"LP E-cores":2,"Threads":10,"Clock base / referência (GHz)":2.0,"Turbo máx. (GHz)":4.2,"Cache L3 (MB)":10,"NPU":"Intel AI Boost","GPU integrada":"Intel Graphics","GPU dedicada":"Não","RAM instalada (GB)":16,"Tipo RAM":"LPDDR5","Velocidade RAM":"até 6400 MT/s","Configuração RAM":"16GB onboard dual-channel","RAM soldada":"Sim","Slots RAM físicos":0,"Slots RAM livres":0,"RAM máxima oficial (GB)":16,"Dual-channel de fábrica":"Sim","Expansão de RAM":"Não","SSD instalado (GB)":512,"Tipo/interface SSD":"NVMe PCIe 4.0 x4","Formato SSD":"M.2 2280","Slots M.2 totais":1,"Slots M.2 livres":0,"Armazenamento máx./observação":"Slot M.2 único; fabricante informa compatibilidade até 1TB","Tela (pol.)":16,"Resolução":"1920×1200","Proporção":"16:10","Painel":"IPS","Acabamento":"Antirreflexo Acer ComfyView","Touch":"Não","Taxa de atualização (Hz)":60,"Brilho (nits)":300,"Cobertura de cores":"45% NTSC","Contraste":"1000:1","Webcam":"Full HD 1080p, até 60 fps","Tampa de privacidade":"N/D","Teclado ABNT2":"Sim","Teclado numérico":"Sim","Teclado retroiluminado":"Não","Touchpad":"Precision Touchpad, resistente à umidade","Wi‑Fi":"Wi‑Fi 6E 2×2","Bluetooth":"5.1 ou superior","Ethernet RJ‑45":"Não","USB‑A":"2× USB 3.2 Gen 1 (5Gbps)","USB‑C":"2× USB‑C","Thunderbolt / USB4":"2× Thunderbolt 4","USB‑C com vídeo":"Sim","USB‑C com carregamento":"Sim","HDMI":"1× HDMI 2.1","Leitor de cartões":"Não","Áudio P2":"1× combo 3,5 mm","Áudio / alto-falantes":"2×2W, Acer TrueHarmony","Microfones":"2×, Purified Voice 2.0","Bateria (Wh)":53,"Células":3,"Autonomia declarada":"Até 8 h","Carregador (W)":65,"Carregamento USB‑C":"Sim","Largura (mm)":360.4,"Profundidade (mm)":253.22,"Espessura (mm)":17.95,"Peso (kg)":1.69,"Material / construção":"Alumínio + plástico (anúncio)","Cor":"Cinza aço","TPM":"fTPM","Trava de segurança":"Kensington","Leitor biométrico":"Não","Garantia informada":"12 meses","Destaques objetivos":"16GB rápidos; 16:10 IPS 300 nits; 2× Thunderbolt 4; webcam FHD; NPU","Limitações / ressalvas":"RAM soldada; sem RJ‑45; sem leitor de cartões; apenas um slot M.2","Link do anúncio":"https://www.mercadolivre.com.br/notebook-16-acer-aspire-16-com-tela-wuxga-ips-1610-processador-intel-core-ultra-5-115u-16gb-ram-lpddr5-a-6400mhz-ssd-de-512gb-windows-11-home/p/MLB60328223","Fonte técnica principal":"https://br-store.acer.com/notebook-acer-a16-71m-55h0--cu5115u--16gb--512gb-ssd--wnhpsl64--gray--lcd-16-nx-jqlal-001/p","Fonte complementar":"https://store.acerempresas.com.br/notebook-acer-a16-71m-55h0--cu5115u--16gb--512gb-ssd--wnhpsl64--gray--lcd-16-nx-jqlal-001/p"
},
{
"Marca":"Lenovo","Modelo / configuração":"ThinkPad E14 (Gen 1) — i7-10510U / 8GB / 512GB","Código / SKU":"20RA/20RB (submodelo não informado)","Ano/geração aproximada":"2019–2020 / Intel 10ª","Sistema operacional":"Não confirmado no anúncio","CPU":"Intel Core i7-10510U","Família / geração CPU":"10ª geração (Comet Lake-U)","Arquitetura CPU":"Convencional","Núcleos":4,"P-cores":4,"E-cores":0,"LP E-cores":0,"Threads":8,"Clock base / referência (GHz)":1.8,"Turbo máx. (GHz)":4.9,"Cache L3 (MB)":8,"NPU":"Não","GPU integrada":"Intel UHD Graphics","GPU dedicada":"Não determinável (família também teve Radeon 625/RX 640)","RAM instalada (GB)":8,"Tipo RAM":"DDR4","Velocidade RAM":"2666 MT/s","Configuração RAM":"1×8GB SO-DIMM (assumido pelo anúncio)","RAM soldada":"Não","Slots RAM físicos":1,"Slots RAM livres":0,"RAM máxima oficial (GB)":16,"Dual-channel de fábrica":"Não (1 slot físico)","Expansão de RAM":"Sim, substituindo módulo; até 16GB oficial","SSD instalado (GB)":512,"Tipo/interface SSD":"NVMe PCIe 3.0 (família)","Formato SSD":"M.2 2242/2280 conforme submodelo","Slots M.2 totais":1,"Slots M.2 livres":0,"Armazenamento máx./observação":"Até 2 unidades: 1× M.2 + 1× 2,5” SATA, conforme configuração física","Tela (pol.)":14,"Resolução":"1920×1080","Proporção":"16:9","Painel":"TN 220 nits OU IPS 250 nits","Acabamento":"Antirreflexo","Touch":"Não","Taxa de atualização (Hz)":60,"Brilho (nits)":"220 ou 250","Cobertura de cores":"N/D","Contraste":"400:1 (TN) / 700:1 (IPS)","Webcam":"720p","Tampa de privacidade":"Varia por submodelo","Teclado ABNT2":"Provável; confirmar unidade","Teclado numérico":"Não","Teclado retroiluminado":"Opcional / não determinável","Touchpad":"ThinkPad TrackPad + TrackPoint","Wi‑Fi":"Wi‑Fi 5 ou Wi‑Fi 6 conforme placa","Bluetooth":"Conforme placa WLAN","Ethernet RJ‑45":"Sim, Gigabit","USB‑A":"2× USB 3.1 Gen1 + 1× USB 2.0","USB‑C":"1× USB‑C 3.1 Gen1","Thunderbolt / USB4":"Não","USB‑C com vídeo":"Sim (DisplayPort)","USB‑C com carregamento":"Sim","HDMI":"1× HDMI 1.4b","Leitor de cartões":"Não","Áudio P2":"1× combo 3,5 mm","Áudio / alto-falantes":"2×2W, Dolby Advanced Audio","Microfones":"2× array","Bateria (Wh)":45,"Células":"Integrada","Autonomia declarada":"Até 12,8 h (MobileMark 2014; família)","Carregador (W)":65,"Carregamento USB‑C":"Sim","Largura (mm)":325,"Profundidade (mm)":232,"Espessura (mm)":17.9,"Peso (kg)":1.69,"Material / construção":"Varia por tampa; chassi corporativo ThinkPad","Cor":"Preto","TPM":"Sim","Trava de segurança":"Kensington","Leitor biométrico":"Opcional / não determinável","Garantia informada":"Depende do vendedor/estado do equipamento","Destaques objetivos":"Teclado/TrackPoint corporativo; RJ‑45; USB‑C com vídeo/carga; possibilidade de 2º drive SATA","Limitações / ressalvas":"Modelo antigo; submodelo não informado impede determinar painel, WLAN, dGPU e biometria; bateria pode ter desgaste se usado/recondicionado","Link do anúncio":"https://www.mercadolivre.com.br/notebook-lenovo-thinkpad-e14-core-i7-10-8gb-ram-512gb-ssd/up/MLBU3626973561","Fonte técnica principal":"https://psref.lenovo.com/syspool/Sys/PDF/ThinkPad/ThinkPad_E14/ThinkPad_E14_Spec.pdf","Fonte complementar":"https://psref.lenovo.com/syspool/Sys/i_pdf/psref562.pdf"
},
{
"Marca":"ASUS","Modelo / configuração":"Vivobook 16 X1605VA-MB763W — i7-1355U / 16GB / 512GB","Código / SKU":"X1605VA-MB763W","Ano/geração aproximada":"2023 / Intel 13ª","Sistema operacional":"Windows 11 Home","CPU":"Intel Core i7-1355U","Família / geração CPU":"13ª geração (Raptor Lake-U)","Arquitetura CPU":"Híbrida","Núcleos":10,"P-cores":2,"E-cores":8,"LP E-cores":0,"Threads":12,"Clock base / referência (GHz)":1.7,"Turbo máx. (GHz)":5.0,"Cache L3 (MB)":12,"NPU":"Não","GPU integrada":"Intel Iris Xe Graphics","GPU dedicada":"Não","RAM instalada (GB)":16,"Tipo RAM":"DDR4","Velocidade RAM":"3200 MT/s","Configuração RAM":"8GB onboard + 8GB SO-DIMM","RAM soldada":"Parcial (8GB)","Slots RAM físicos":1,"Slots RAM livres":0,"RAM máxima oficial (GB)":16,"Dual-channel de fábrica":"Sim","Expansão de RAM":"Limitada; 8GB soldados + 1 SO-DIMM, máximo oficial 16GB","SSD instalado (GB)":512,"Tipo/interface SSD":"NVMe M.2","Formato SSD":"M.2","Slots M.2 totais":1,"Slots M.2 livres":0,"Armazenamento máx./observação":"1 slot M.2; capacidade depende de SSD substituto","Tela (pol.)":16,"Resolução":"1920×1200","Proporção":"16:10","Painel":"IPS-level","Acabamento":"Antirreflexo","Touch":"Não","Taxa de atualização (Hz)":60,"Brilho (nits)":300,"Cobertura de cores":"45% NTSC","Contraste":"N/D","Webcam":"HD 720p","Tampa de privacidade":"Sim","Teclado ABNT2":"Sim (SKU BR)","Teclado numérico":"Sim","Teclado retroiluminado":"Não","Touchpad":"Precision touchpad","Wi‑Fi":"Wi‑Fi 5 (802.11ac) 1×1","Bluetooth":"5.1","Ethernet RJ‑45":"Não","USB‑A":"2× USB 3.2 Gen1 + 1× USB 2.0","USB‑C":"1× USB 3.2 Gen1 Type‑C","Thunderbolt / USB4":"Não","USB‑C com vídeo":"Não confirmado","USB‑C com carregamento":"Sim (Power Delivery)","HDMI":"1× HDMI 1.4","Leitor de cartões":"Não","Áudio P2":"1× combo 3,5 mm","Áudio / alto-falantes":"SonicMaster estéreo","Microfones":"Integrados; AI Noise Canceling","Bateria (Wh)":42,"Células":3,"Autonomia declarada":"N/D","Carregador (W)":45,"Carregamento USB‑C":"SKU suporta PD, mas inclui carregador DC-in","Largura (mm)":358.7,"Profundidade (mm)":249.5,"Espessura (mm)":19.9,"Peso (kg)":1.88,"Material / construção":"Plástico (família)","Cor":"Cool Silver","TPM":"Firmware TPM","Trava de segurança":"N/D","Leitor biométrico":"Não informado","Garantia informada":"12 meses","Destaques objetivos":"i7-1355U; 16GB em dual-channel; tela 16:10 300 nits; tampa física da webcam","Limitações / ressalvas":"Wi‑Fi 5 1×1; HDMI 1.4; bateria de 42Wh; expansão de RAM limitada a 16GB oficial","Link do anúncio":"https://www.mercadolivre.com.br/notebook-vivobook-16-intel-core-i7-1355u-16gb-ram-512gb-ssd-tela-16-full-hd-windows-11-asus/p/MLB39460220","Fonte técnica principal":"https://b2b.lojaasus.com.br/notebook-asus-vivobook-16-x1605va-mb763w-cool-silver.html","Fonte complementar":"https://www.asus.com/br/laptops/for-home/vivobook/vivobook-16-x1605/techspec/"
},
{
"Marca":"HP","Modelo / configuração":"200 G2i 16” — Core 5 120U / 8GB / 512GB","Código / SKU":"E30QFAT#AK4","Ano/geração aproximada":"2025–2026 / Core Série 1","Sistema operacional":"Windows 11 Home Single Language","CPU":"Intel Core 5 120U","Família / geração CPU":"Intel Core Série 1 (Raptor Lake-U refresh)","Arquitetura CPU":"Híbrida","Núcleos":10,"P-cores":2,"E-cores":8,"LP E-cores":0,"Threads":12,"Clock base / referência (GHz)":1.4,"Turbo máx. (GHz)":5.0,"Cache L3 (MB)":12,"NPU":"Não","GPU integrada":"Intel Graphics","GPU dedicada":"Não","RAM instalada (GB)":8,"Tipo RAM":"DDR5","Velocidade RAM":"5200 MT/s","Configuração RAM":"1×8GB SO-DIMM","RAM soldada":"Não","Slots RAM físicos":2,"Slots RAM livres":1,"RAM máxima oficial (GB)":32,"Dual-channel de fábrica":"Não","Expansão de RAM":"Sim; até 32GB oficial","SSD instalado (GB)":512,"Tipo/interface SSD":"PCIe Gen4 NVMe","Formato SSD":"M.2","Slots M.2 totais":1,"Slots M.2 livres":0,"Armazenamento máx./observação":"Família oferece SSDs até 1TB; substituir SSD para ampliar","Tela (pol.)":16,"Resolução":"1920×1200","Proporção":"16:10","Painel":"IPS / UWVA","Acabamento":"Antirreflexo","Touch":"Não","Taxa de atualização (Hz)":60,"Brilho (nits)":300,"Cobertura de cores":"62,5% sRGB","Contraste":"N/D","Webcam":"FHD 1080p HDR (família/configuração correspondente)","Tampa de privacidade":"N/D","Teclado ABNT2":"Sim (SKU BR)","Teclado numérico":"Sim","Teclado retroiluminado":"Não informado","Touchpad":"Clickpad multitoque","Wi‑Fi":"Wi‑Fi 6 (Realtek 8852BE-VT, configuração comum)","Bluetooth":"5.4 (com Wi‑Fi 6)","Ethernet RJ‑45":"Sim, Gigabit","USB‑A":"2× USB 3.2 Gen1","USB‑C":"2× USB 3.2 Gen2 Type‑C 10Gbps","Thunderbolt / USB4":"Não","USB‑C com vídeo":"Sim, DisplayPort 1.4","USB‑C com carregamento":"Sim, USB Power Delivery","HDMI":"1× HDMI 1.4b","Leitor de cartões":"Não informado","Áudio P2":"1× combo 3,5 mm","Áudio / alto-falantes":"Poly Studio, 2 estéreo","Microfones":"2× array, redução de ruído por IA","Bateria (Wh)":41,"Células":3,"Autonomia declarada":"N/D","Carregador (W)":65,"Carregamento USB‑C":"Sim","Largura (mm)":358.6,"Profundidade (mm)":251.8,"Espessura (mm)":18.9,"Peso (kg)":1.72,"Material / construção":"Plástico / linha corporativa básica","Cor":"Prata","TPM":"Sim","Trava de segurança":"Sim","Leitor biométrico":"Não informado","Garantia informada":"12 meses (confirmar anúncio)","Destaques objetivos":"RAM expansível até 32GB; 2× USB‑C 10Gbps com DP/PD; RJ‑45; tela 16:10 300 nits; webcam FHD","Limitações / ressalvas":"8GB em single-channel de fábrica; bateria 41Wh; algumas características variam por WLAN/lote","Link do anúncio":"https://www.mercadolivre.com.br/notebook-hp-200-g2i-intel-core-5-120u-16-intel-graphics-ram-8gb-1x8gb-ddr5-5200-ssd-512gb-pcie4x4-windows-11-home-sl-e30qfatak4/p/MLB78311028","Fonte técnica principal":"https://support.hp.com/br-pt/document/ish_13834797-13835475-16","Fonte complementar":"https://www.hp.com/za-en/products/laptops/product-details/product-specifications/2104283715"
},
{
"Marca":"Dell","Modelo / configuração":"Dell 15 DC15-I51334U-A50 — i5-1334U / 8GB / 512GB","Código / SKU":"DC15-I51334U-A50 / 210-BWBG","Ano/geração aproximada":"2026 / Intel 13ª","Sistema operacional":"Windows 11 Home","CPU":"Intel Core i5-1334U","Família / geração CPU":"13ª geração (Raptor Lake-U)","Arquitetura CPU":"Híbrida","Núcleos":10,"P-cores":2,"E-cores":8,"LP E-cores":0,"Threads":12,"Clock base / referência (GHz)":0.9,"Turbo máx. (GHz)":4.6,"Cache L3 (MB)":12,"NPU":"Não","GPU integrada":"Intel UHD Graphics (ficha comercial)","GPU dedicada":"Não","RAM instalada (GB)":8,"Tipo RAM":"DDR5","Velocidade RAM":"4400 MT/s","Configuração RAM":"1×8GB SO-DIMM","RAM soldada":"Não","Slots RAM físicos":2,"Slots RAM livres":1,"RAM máxima oficial (GB)":16,"Dual-channel de fábrica":"Não","Expansão de RAM":"Sim; até 16GB informado","SSD instalado (GB)":512,"Tipo/interface SSD":"PCIe NVMe","Formato SSD":"M.2","Slots M.2 totais":1,"Slots M.2 livres":0,"Armazenamento máx./observação":"Substituição do M.2 para ampliar","Tela (pol.)":15.6,"Resolução":"1920×1080","Proporção":"16:9","Painel":"WVA","Acabamento":"Antirreflexo","Touch":"Não","Taxa de atualização (Hz)":120,"Brilho (nits)":250,"Cobertura de cores":"N/D","Contraste":"600:1","Webcam":"HD 720p widescreen","Tampa de privacidade":"N/D","Teclado ABNT2":"Sim","Teclado numérico":"Sim","Teclado retroiluminado":"Não","Touchpad":"Precision touchpad","Wi‑Fi":"Wi‑Fi 6 Realtek RTL8852BE 2×2","Bluetooth":"Sim (placa combinada)","Ethernet RJ‑45":"Não","USB‑A":"1× USB 3.2 Gen1 + 1× USB 2.0","USB‑C":"1× USB 3.2 Gen1 Type‑C (dados)","Thunderbolt / USB4":"Não","USB‑C com vídeo":"Não","USB‑C com carregamento":"Não","HDMI":"1× HDMI 1.4","Leitor de cartões":"SD","Áudio P2":"1× combo 3,5 mm","Áudio / alto-falantes":"Waves MaxxAudio Pro","Microfones":"1× digital","Bateria (Wh)":41,"Células":3,"Autonomia declarada":"Não especificada","Carregador (W)":65,"Carregamento USB‑C":"Não","Largura (mm)":358.5,"Profundidade (mm)":235.5,"Espessura (mm)":18.9,"Peso (kg)":1.63,"Material / construção":"Plástico","Cor":"Preto Carbono","TPM":"Sim","Trava de segurança":"N/D","Leitor biométrico":"Não","Garantia informada":"12 meses","Destaques objetivos":"Tela 120Hz; RAM expansível; leitor SD; peso relativamente baixo","Limitações / ressalvas":"8GB single-channel; USB‑C apenas dados; sem RJ‑45; bateria 41Wh; limite oficial de RAM 16GB","Link do anúncio":"https://www.mercadolivre.com.br/notebook-dell-dc15-i51334u-a50-156-fhd-i5-8gb-512gb-win-11/p/MLB70040749","Fonte técnica principal":"https://www.magazineluiza.com.br/notebook-dell-15-dc15-i51334u-a50-intel-core-i5-8gb-ram-512gb-ssd-156-full-hd-windows-11-210-bwbg/p/241623300/in/nodl/","Fonte complementar":"https://quenotebookcomprar.com.br/dell-15-dc15-i51334u-a50/"
},
{
"Marca":"Dell","Modelo / configuração":"Dell 15 DC15-I51334U-M80 — i5-1334U / 16GB / 1TB","Código / SKU":"DC15-I51334U-M80","Ano/geração aproximada":"2026 / Intel 13ª","Sistema operacional":"Windows 11 Home","CPU":"Intel Core i5-1334U","Família / geração CPU":"13ª geração (Raptor Lake-U)","Arquitetura CPU":"Híbrida","Núcleos":10,"P-cores":2,"E-cores":8,"LP E-cores":0,"Threads":12,"Clock base / referência (GHz)":0.9,"Turbo máx. (GHz)":4.6,"Cache L3 (MB)":12,"NPU":"Não","GPU integrada":"Intel UHD Graphics (ficha comercial)","GPU dedicada":"Não","RAM instalada (GB)":16,"Tipo RAM":"DDR5","Velocidade RAM":"4400 MT/s","Configuração RAM":"1×16GB SO-DIMM","RAM soldada":"Não","Slots RAM físicos":2,"Slots RAM livres":1,"RAM máxima oficial (GB)":16,"Dual-channel de fábrica":"Não (1×16GB)","Expansão de RAM":"Limite de 16GB informado; slot físico livre sem ganho oficial de capacidade","SSD instalado (GB)":1024,"Tipo/interface SSD":"PCIe NVMe","Formato SSD":"M.2","Slots M.2 totais":1,"Slots M.2 livres":0,"Armazenamento máx./observação":"1TB de fábrica; ampliar requer substituição","Tela (pol.)":15.6,"Resolução":"1920×1080","Proporção":"16:9","Painel":"WVA","Acabamento":"Antirreflexo","Touch":"Não","Taxa de atualização (Hz)":120,"Brilho (nits)":250,"Cobertura de cores":"N/D","Contraste":"600:1","Webcam":"HD 720p widescreen","Tampa de privacidade":"N/D","Teclado ABNT2":"Sim","Teclado numérico":"Sim","Teclado retroiluminado":"Não","Touchpad":"Precision touchpad","Wi‑Fi":"Wi‑Fi 6 Realtek RTL8852BE 2×2","Bluetooth":"Sim (placa combinada)","Ethernet RJ‑45":"Não","USB‑A":"1× USB 3.2 Gen1 + 1× USB 2.0","USB‑C":"1× USB 3.2 Gen1 Type‑C (dados)","Thunderbolt / USB4":"Não","USB‑C com vídeo":"Não","USB‑C com carregamento":"Não","HDMI":"1× HDMI 1.4","Leitor de cartões":"SD","Áudio P2":"1× combo 3,5 mm","Áudio / alto-falantes":"Waves MaxxAudio Pro","Microfones":"1× digital","Bateria (Wh)":41,"Células":3,"Autonomia declarada":"Não especificada","Carregador (W)":65,"Carregamento USB‑C":"Não","Largura (mm)":358.5,"Profundidade (mm)":235.5,"Espessura (mm)":18.9,"Peso (kg)":1.63,"Material / construção":"Plástico","Cor":"Preto Carbono","TPM":"Sim","Trava de segurança":"N/D","Leitor biométrico":"Não","Garantia informada":"12 meses","Destaques objetivos":"16GB e 1TB de fábrica; tela 120Hz; leitor SD; peso relativamente baixo","Limitações / ressalvas":"16GB em módulo único; USB‑C apenas dados; sem RJ‑45; bateria 41Wh; limite de RAM oficial já atingido","Link do anúncio":"https://www.mercadolivre.com.br/dell-inspiron-dc15-i51334u-m80-notebook-156-i5-16gb-1tb-ssd-tela-antirreflexo/p/MLB76590114","Fonte técnica principal":"https://www.magazineluiza.com.br/notebook-dell-15-dc15-i51334u-m80-15-6-full-hd-13a-gen-intel-core-i5-16gb-1tb-ssd-win-11-preto-carbono/p/jc0448k2f9/in/nodl/","Fonte complementar":"https://www.kabum.com.br/produto/1028017/notebook-dell-inspiron-dc15-i51334u-m80-15-6-full-hd-13-gen-intel-core-i5-16gb-1tb-ssd-win-11-preto-carbono"
}
]

SUMMARY = {
"Samsung Galaxy Book4":"Leve, bateria de 54 Wh, RJ‑45, dois USB‑C e segundo slot M.2. A limitação mais importante é a RAM de 8 GB soldada.",
"Acer Aspire 16":"Conjunto moderno com 16 GB LPDDR5, tela 16:10 de 300 nits, Thunderbolt 4, webcam FHD e NPU. RAM não é expansível.",
"Lenovo ThinkPad E14":"Construção e ergonomia corporativa, RJ‑45 e USB‑C com vídeo/carga. É uma plataforma muito mais antiga; submodelo incompleto gera incerteza.",
"ASUS Vivobook 16":"i7-1355U, 16 GB em dual-channel e tela 16:10 de 300 nits. Bateria pequena e conectividade menos moderna.",
"HP 200 G2i":"RAM DDR5 expansível até 32 GB, dois USB‑C 10 Gbps com vídeo/carga, RJ‑45 e webcam FHD. Sai de fábrica com 8 GB single-channel.",
"Dell A50":"Tela 120 Hz e RAM expansível, mas apenas 8 GB de fábrica, USB‑C somente dados e bateria de 41 Wh.",
"Dell M80":"Mesmo chassi do A50, com 16 GB e SSD de 1 TB. Tela 120 Hz; USB‑C continua limitado a dados e a bateria é de 41 Wh."
}

df = pd.DataFrame(NOTEBOOKS)
MODEL_COL = "Modelo / configuração"
MODELS = df[MODEL_COL].tolist()

GROUPS = {
"Identificação":["Marca","Modelo / configuração","Código / SKU","Ano/geração aproximada","Sistema operacional"],
"Processador e gráficos":["CPU","Família / geração CPU","Arquitetura CPU","Núcleos","P-cores","E-cores","LP E-cores","Threads","Clock base / referência (GHz)","Turbo máx. (GHz)","Cache L3 (MB)","NPU","GPU integrada","GPU dedicada"],
"Memória":["RAM instalada (GB)","Tipo RAM","Velocidade RAM","Configuração RAM","RAM soldada","Slots RAM físicos","Slots RAM livres","RAM máxima oficial (GB)","Dual-channel de fábrica","Expansão de RAM"],
"Armazenamento":["SSD instalado (GB)","Tipo/interface SSD","Formato SSD","Slots M.2 totais","Slots M.2 livres","Armazenamento máx./observação"],
"Tela":["Tela (pol.)","Resolução","Proporção","Painel","Acabamento","Touch","Taxa de atualização (Hz)","Brilho (nits)","Cobertura de cores","Contraste"],
"Câmera e entrada":["Webcam","Tampa de privacidade","Teclado ABNT2","Teclado numérico","Teclado retroiluminado","Touchpad"],
"Conectividade":["Wi‑Fi","Bluetooth","Ethernet RJ‑45","USB‑A","USB‑C","Thunderbolt / USB4","USB‑C com vídeo","USB‑C com carregamento","HDMI","Leitor de cartões","Áudio P2"],
"Áudio":["Áudio / alto-falantes","Microfones"],
"Bateria e energia":["Bateria (Wh)","Células","Autonomia declarada","Carregador (W)","Carregamento USB‑C"],
"Dimensões e construção":["Largura (mm)","Profundidade (mm)","Espessura (mm)","Peso (kg)","Material / construção","Cor"],
"Segurança e suporte":["TPM","Trava de segurança","Leitor biométrico","Garantia informada"],
"Observações e fontes":["Destaques objetivos","Limitações / ressalvas","Link do anúncio","Fonte técnica principal","Fonte complementar"],
}
ALL_CRITERIA = [c for cols in GROUPS.values() for c in cols]

DEFAULT_WEIGHTS = {c: 0 for c in ALL_CRITERIA}
DEFAULT_WEIGHTS.update({
"CPU":8,"Núcleos":3,"Threads":3,"Turbo máx. (GHz)":3,"NPU":2,"GPU integrada":3,
"RAM instalada (GB)":8,"Tipo RAM":3,"Velocidade RAM":3,"Dual-channel de fábrica":4,"Expansão de RAM":6,"RAM máxima oficial (GB)":4,
"SSD instalado (GB)":5,"Tipo/interface SSD":3,"Slots M.2 livres":4,
"Resolução":5,"Proporção":3,"Painel":6,"Taxa de atualização (Hz)":3,"Brilho (nits)":5,"Cobertura de cores":4,
"Webcam":3,"Tampa de privacidade":2,"Teclado retroiluminado":2,
"Wi‑Fi":4,"Ethernet RJ‑45":2,"USB‑C":3,"Thunderbolt / USB4":4,"USB‑C com vídeo":4,"USB‑C com carregamento":4,"HDMI":2,"Leitor de cartões":1,
"Bateria (Wh)":8,"Carregamento USB‑C":3,"Peso (kg)":7,"Espessura (mm)":2,"Material / construção":4,
"Leitor biométrico":2,"Garantia informada":2,
})

CPU_SCORE = {"Intel Core Ultra 5 115U":8.2,"Intel Core 5 120U":8.4,"Intel Core i7-1355U":8.5,"Intel Core i5-1335U":7.7,"Intel Core i5-1334U":7.5,"Intel Core i7-10510U":5.2}
GPU_SCORE = {"Intel Iris Xe Graphics":7.5,"Intel Graphics":7.2,"Intel UHD Graphics":5.0,"Intel UHD Graphics (ficha comercial)":5.5}

def text_score(v):
    s=str(v).lower()
    if s in {"n/d","não informado","não confirmado","none","nan"}: return 5.0
    if "não determin" in s or "varia " in s or "opcional" in s: return 5.0
    if s.startswith("sim") or "gigabit" in s or "power delivery" in s or "displayport" in s: return 8.5
    if s == "não": return 3.0
    return 6.5

def numeric_scores(series, lower_is_better=False):
    x=pd.to_numeric(series, errors="coerce")
    if x.notna().sum() < 2 or x.max()==x.min():
        return pd.Series([7.0 if pd.notna(v) else 5.0 for v in x], index=series.index)
    z=(x-x.min())/(x.max()-x.min())
    if lower_is_better: z=1-z
    return 4.0 + z*6.0

LOWER_BETTER={"Peso (kg)","Espessura (mm)","Largura (mm)","Profundidade (mm)"}

def initial_scores():
    out=pd.DataFrame(index=MODELS, columns=ALL_CRITERIA, dtype=float)
    for c in ALL_CRITERIA:
        if pd.api.types.is_numeric_dtype(df[c]):
            out[c]=numeric_scores(df[c], c in LOWER_BETTER).values
        else:
            out[c]=df[c].map(text_score).values
    out["CPU"]=df["CPU"].map(CPU_SCORE).fillna(6.0).values
    out["GPU integrada"]=df["GPU integrada"].map(GPU_SCORE).fillna(6.0).values
    # Rubricas úteis para campos textuais de alta relevância
    out["Expansão de RAM"]=[2,2,7,5,10,8,5]
    out["Tipo RAM"]=[6.5,9,6,6,9,9,9]
    out["Dual-channel de fábrica"]=[8.5,9,3,9,3,3,3]
    out["Painel"]=[8,9,5.5,8.5,9,7.5,7.5]
    out["Resolução"]=[7,9,7,9,9,7,7]
    out["Proporção"]=[6,9,6,9,9,6,6]
    out["Cobertura de cores"]=[5,6,5,6,7,5,5]
    out["Webcam"]=[6,9,5.5,6,9,5.5,5.5]
    out["Wi‑Fi"]=[8,9.5,6,5.5,8.5,8.5,8.5]
    out["Thunderbolt / USB4"]=[5,10,3,3,3,3,3]
    out["USB‑C com vídeo"]=[8,10,8,5,9,3,3]
    out["USB‑C com carregamento"]=[9,10,9,8,10,3,3]
    out["Material / construção"]=[9,8,8,6,6,6,6]
    return out.clip(0,10).round(1)

if "weights" not in st.session_state: st.session_state.weights = DEFAULT_WEIGHTS.copy()
if "scores" not in st.session_state: st.session_state.scores = initial_scores()

PRESETS = {
"Equilibrado": DEFAULT_WEIGHTS,
"Mobilidade": {**DEFAULT_WEIGHTS, "Peso (kg)":10,"Bateria (Wh)":10,"Espessura (mm)":7,"Carregamento USB‑C":7,"Tela (pol.)":2,"Taxa de atualização (Hz)":1},
"Trabalho / produtividade": {**DEFAULT_WEIGHTS, "RAM instalada (GB)":10,"Expansão de RAM":9,"CPU":9,"Tela (pol.)":6,"Proporção":7,"Webcam":6,"Ethernet RJ‑45":5,"Bateria (Wh)":7},
"Desempenho": {**DEFAULT_WEIGHTS, "CPU":10,"Núcleos":7,"Threads":7,"RAM instalada (GB)":10,"Tipo RAM":6,"Velocidade RAM":7,"GPU integrada":7,"SSD instalado (GB)":6},
"Tela e multimídia": {**DEFAULT_WEIGHTS, "Painel":10,"Resolução":9,"Brilho (nits)":9,"Cobertura de cores":10,"Taxa de atualização (Hz)":7,"Áudio / alto-falantes":5},
"Expansão / longevidade": {**DEFAULT_WEIGHTS, "Expansão de RAM":10,"RAM máxima oficial (GB)":10,"Slots RAM livres":8,"Slots M.2 livres":9,"Armazenamento máx./observação":7,"Tipo/interface SSD":6},
}

def ranking():
    weights=pd.Series(st.session_state.weights, dtype=float)
    active=weights[weights>0]
    if active.empty:
        total=pd.Series(0.0,index=MODELS)
    else:
        total=st.session_state.scores[active.index].mul(active,axis=1).sum(axis=1)/active.sum()
    result=pd.DataFrame({"Notebook":MODELS,"Pontuação":total.values})
    result["Nota / 100"]=(result["Pontuação"]*10).round(1)
    return result.sort_values("Pontuação",ascending=False).reset_index(drop=True)

st.title("Nota da Lu")
st.caption("Comparador interativo de notebooks • pesos, notas e especificações manipuláveis")

with st.sidebar:
    st.subheader("Perfil de compra")
    preset=st.selectbox("Preset de pesos", list(PRESETS))
    if st.button("Aplicar preset", use_container_width=True):
        st.session_state.weights=PRESETS[preset].copy()
        st.rerun()
    if st.button("Restaurar tudo", use_container_width=True):
        st.session_state.weights=DEFAULT_WEIGHTS.copy()
        st.session_state.scores=initial_scores()
        st.rerun()
    st.divider()
    selected=st.multiselect("Notebooks visíveis", MODELS, default=MODELS)
    st.caption("Pesos 0 = critério fora do ranking. Notas vão de 0 a 10.")

tabs=st.tabs(["🏆 Ranking","⚖️ Pesos","🎚️ Notas","🧾 Ficha completa","📝 Resumo"])

with tabs[0]:
    rank=ranking()
    rank=rank[rank["Notebook"].isin(selected)]
    if len(rank):
        winner=rank.iloc[0]
        c1,c2,c3,c4=st.columns(4)
        c1.metric("1º no seu perfil", winner["Notebook"].split(" — ")[0])
        c2.metric("Nota", f'{winner["Nota / 100"]:.1f}/100')
        c3.metric("Critérios ativos", sum(v>0 for v in st.session_state.weights.values()))
        c4.metric("Modelos comparados", len(rank))
        fig=px.bar(rank.sort_values("Pontuação"),x="Nota / 100",y="Notebook",orientation="h",text="Nota / 100",range_x=[0,100])
        fig.update_layout(height=430,margin=dict(l=10,r=20,t=20,b=10),xaxis_title="Pontuação ponderada",yaxis_title="")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(rank[["Notebook","Nota / 100"]],hide_index=True,use_container_width=True)
        st.download_button("Baixar ranking em CSV", rank.to_csv(index=False).encode("utf-8-sig"),"ranking_notebooks.csv","text/csv")
        st.info("A pontuação é uma média ponderada das notas que você controla. Ela não pretende substituir preço, preferência pessoal ou inspeção do anúncio.")

with tabs[1]:
    st.subheader("Peso de cada critério")
    st.caption("0 ignora o critério; 10 dá importância máxima. Todos os critérios da planilha aparecem aqui, inclusive os descritivos.")
    group=st.selectbox("Filtrar grupo",["Todos"]+list(GROUPS))
    visible=ALL_CRITERIA if group=="Todos" else GROUPS[group]
    weight_df=pd.DataFrame({"Critério":visible,"Peso":[st.session_state.weights[c] for c in visible]})
    edited=st.data_editor(weight_df,hide_index=True,use_container_width=True,
        column_config={"Peso":st.column_config.NumberColumn(min_value=0,max_value=10,step=1,format="%d")},
        disabled=["Critério"],key=f"weight_editor_{group}")
    if st.button("Aplicar pesos editados"):
        for _,r in edited.iterrows(): st.session_state.weights[r["Critério"]]=float(r["Peso"])
        st.rerun()

with tabs[2]:
    st.subheader("Nota de cada característica")
    st.caption("As notas iniciais são uma heurística para dar um ponto de partida. Você pode sobrescrever qualquer célula.")
    group2=st.selectbox("Grupo de critérios",list(GROUPS),key="score_group")
    score_cols=[c for c in GROUPS[group2] if c not in ["Marca","Modelo / configuração","Link do anúncio","Fonte técnica principal","Fonte complementar"]]
    score_edit=st.session_state.scores[score_cols].copy()
    score_edit.insert(0,"Notebook",score_edit.index)
    score_edit=score_edit[score_edit["Notebook"].isin(selected)]
    edited_scores=st.data_editor(score_edit,hide_index=True,use_container_width=True,
        column_config={c:st.column_config.NumberColumn(min_value=0.0,max_value=10.0,step=.1,format="%.1f") for c in score_cols},
        disabled=["Notebook"],key=f"score_editor_{group2}")
    if st.button("Aplicar notas editadas"):
        for _,r in edited_scores.iterrows():
            m=r["Notebook"]
            for c in score_cols: st.session_state.scores.loc[m,c]=float(r[c])
        st.rerun()

with tabs[3]:
    st.subheader("Ficha técnica completa")
    compare=st.multiselect("Escolha até 4 para comparar lado a lado", MODELS, default=MODELS[:3], max_selections=4)
    full=df[df[MODEL_COL].isin(compare)].set_index(MODEL_COL).T
    group3=st.selectbox("Mostrar grupo",["Todos"]+list(GROUPS),key="spec_group")
    if group3!="Todos":
        wanted=[c for c in GROUPS[group3] if c!=MODEL_COL]
        full=full.loc[[c for c in wanted if c in full.index]]
    st.dataframe(full,use_container_width=True,height=700)
    st.download_button("Baixar specs em CSV",df.to_csv(index=False).encode("utf-8-sig"),"notebooks_specs.csv","text/csv")

with tabs[4]:
    st.subheader("Resumo executivo")
    cards=[
        ("Samsung Galaxy Book4",SUMMARY["Samsung Galaxy Book4"]),
        ("Acer Aspire 16",SUMMARY["Acer Aspire 16"]),
        ("Lenovo ThinkPad E14",SUMMARY["Lenovo ThinkPad E14"]),
        ("ASUS Vivobook 16",SUMMARY["ASUS Vivobook 16"]),
        ("HP 200 G2i",SUMMARY["HP 200 G2i"]),
        ("Dell A50",SUMMARY["Dell A50"]),
        ("Dell M80",SUMMARY["Dell M80"]),
    ]
    for title,body in cards:
        with st.container(border=True):
            st.markdown(f"### {title}")
            st.write(body)
    st.divider()
    st.markdown("**Notas metodológicas**")
    st.write("• N/D significa dado não confirmado com segurança. • No ThinkPad E14, a ausência do MTM/submodelo completo impede cravar painel, WLAN, GPU dedicada e biometria. • Preços não entram no ranking porque variam rapidamente; podem ser adicionados depois como critério.")
