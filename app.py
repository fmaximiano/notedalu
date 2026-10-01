import json
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

# ---------------------------------------------------------------------
# Estrutura de critérios e modelo de decisão
# ---------------------------------------------------------------------
MODEL_COL = "Modelo / configuração"
EXTRA_COLUMNS = ["GPU", "Preço atual (R$)"]
SPEC_COLUMNS = list(NOTEBOOKS[0].keys()) + [c for c in EXTRA_COLUMNS if c not in NOTEBOOKS[0]]

GROUPS = {
    "Identificação":["Marca","Modelo / configuração","Código / SKU","Ano/geração aproximada","Sistema operacional"],
    "Compra":["Preço atual (R$)"],
    "Processador e gráficos":["CPU","Família / geração CPU","Arquitetura CPU","Núcleos","P-cores","E-cores","LP E-cores","Threads","Clock base / referência (GHz)","Turbo máx. (GHz)","Cache L3 (MB)","NPU","GPU","GPU integrada","GPU dedicada"],
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

IMPORTANT_CRITERIA = [
    "Preço atual (R$)",
    "CPU","GPU",
    "RAM instalada (GB)","Tipo RAM","Dual-channel de fábrica","Expansão de RAM","RAM máxima oficial (GB)",
    "SSD instalado (GB)","Tipo/interface SSD","Slots M.2 livres",
    "Resolução","Proporção","Painel","Taxa de atualização (Hz)","Brilho (nits)","Cobertura de cores",
    "Webcam","Wi‑Fi","Thunderbolt / USB4","USB‑C com vídeo","USB‑C com carregamento",
    "Bateria (Wh)","Peso (kg)","Material / construção",
]

IMPORTANT_GROUPS = {
    "Preço e valor":["Preço atual (R$)"],
    "Desempenho":["CPU","GPU"],
    "Memória":["RAM instalada (GB)","Tipo RAM","Dual-channel de fábrica","Expansão de RAM","RAM máxima oficial (GB)"],
    "Armazenamento":["SSD instalado (GB)","Tipo/interface SSD","Slots M.2 livres"],
    "Tela":["Resolução","Proporção","Painel","Taxa de atualização (Hz)","Brilho (nits)","Cobertura de cores"],
    "Comunicação e portas":["Webcam","Wi‑Fi","Thunderbolt / USB4","USB‑C com vídeo","USB‑C com carregamento"],
    "Mobilidade e construção":["Bateria (Wh)","Peso (kg)","Material / construção"],
}

DEFAULT_WEIGHTS = {
    "Preço atual (R$)":9,
    "CPU":9,"GPU":4,
    "RAM instalada (GB)":9,"Tipo RAM":4,"Dual-channel de fábrica":5,"Expansão de RAM":7,"RAM máxima oficial (GB)":5,
    "SSD instalado (GB)":5,"Tipo/interface SSD":4,"Slots M.2 livres":4,
    "Resolução":6,"Proporção":4,"Painel":7,"Taxa de atualização (Hz)":3,"Brilho (nits)":6,"Cobertura de cores":4,
    "Webcam":3,"Wi‑Fi":4,"Thunderbolt / USB4":4,"USB‑C com vídeo":4,"USB‑C com carregamento":5,
    "Bateria (Wh)":8,"Peso (kg)":7,"Material / construção":4,
}

PRESETS = {
    "Equilibrado": DEFAULT_WEIGHTS,
    "Custo-benefício": {**DEFAULT_WEIGHTS,"Preço atual (R$)":10,"CPU":8,"RAM instalada (GB)":8,"Painel":6,"Bateria (Wh)":6},
    "Mobilidade": {**DEFAULT_WEIGHTS,"Preço atual (R$)":6,"Bateria (Wh)":10,"Peso (kg)":10,"USB‑C com carregamento":8,"Material / construção":6,"Taxa de atualização (Hz)":1},
    "Trabalho / produtividade": {**DEFAULT_WEIGHTS,"Preço atual (R$)":7,"CPU":9,"RAM instalada (GB)":10,"Expansão de RAM":9,"Painel":8,"Proporção":7,"Webcam":6,"Bateria (Wh)":7},
    "Desempenho": {**DEFAULT_WEIGHTS,"Preço atual (R$)":5,"CPU":10,"GPU":9,"RAM instalada (GB)":10,"Tipo RAM":7,"Dual-channel de fábrica":7,"SSD instalado (GB)":7},
    "Tela e multimídia": {**DEFAULT_WEIGHTS,"Preço atual (R$)":5,"Painel":10,"Resolução":9,"Brilho (nits)":9,"Cobertura de cores":10,"Taxa de atualização (Hz)":8,"GPU":6},
    "Expansão / longevidade": {**DEFAULT_WEIGHTS,"Preço atual (R$)":6,"Expansão de RAM":10,"RAM máxima oficial (GB)":10,"Slots M.2 livres":9,"Tipo/interface SSD":6,"Material / construção":7},
}

CPU_SCORE = {
    "Intel Core Ultra 5 115U":8.2,"Intel Core 5 120U":8.4,"Intel Core i7-1355U":8.5,
    "Intel Core i5-1335U":7.7,"Intel Core i5-1334U":7.5,"Intel Core i7-10510U":5.2
}
GPU_SCORE = {
    "Intel Iris Xe Graphics":7.5,"Intel Graphics":7.2,
    "Intel UHD Graphics":5.0,"Intel UHD Graphics (ficha comercial)":5.5
}
NUMERIC_FIELDS = {
    "Preço atual (R$)","Núcleos","P-cores","E-cores","LP E-cores","Threads","Clock base / referência (GHz)",
    "Turbo máx. (GHz)","Cache L3 (MB)","RAM instalada (GB)","Slots RAM físicos","Slots RAM livres",
    "RAM máxima oficial (GB)","SSD instalado (GB)","Slots M.2 totais","Slots M.2 livres","Tela (pol.)",
    "Taxa de atualização (Hz)","Brilho (nits)","Bateria (Wh)","Carregador (W)","Largura (mm)",
    "Profundidade (mm)","Espessura (mm)","Peso (kg)"
}
LOWER_BETTER = {"Preço atual (R$)","Peso (kg)"}
UNKNOWN_VALUES = {"","n/d","não informado","não confirmado","none","nan"}

def resolved_gpu(row):
    dedicated = str(row.get("GPU dedicada","N/D")).strip()
    integrated = str(row.get("GPU integrada","N/D")).strip()
    if dedicated.lower() not in UNKNOWN_VALUES and dedicated.lower() != "não" and "não determin" not in dedicated.lower():
        return dedicated
    return integrated

def normalize_row(row):
    item = {c:row.get(c,"N/D") for c in SPEC_COLUMNS}
    if str(item.get("GPU","N/D")).strip().lower() in UNKNOWN_VALUES:
        item["GPU"] = resolved_gpu(row)
    return item

def current_df():
    return pd.DataFrame([normalize_row(row) for row in st.session_state.inventory],columns=SPEC_COLUMNS)

def numeric_scores(series, lower_is_better=False):
    x = pd.to_numeric(series, errors="coerce")
    valid = x.dropna()
    if len(valid) < 2 or valid.max() == valid.min():
        return pd.Series([7.0 if pd.notna(v) else 5.0 for v in x], index=series.index)
    z = (x-valid.min())/(valid.max()-valid.min())
    if lower_is_better:
        z = 1-z
    return (4.0 + z*6.0).fillna(5.0)

def generic_text_score(value):
    s = str(value).strip().lower()
    if s in UNKNOWN_VALUES:
        return 5.0
    if "não determin" in s or "varia " in s or "opcional" in s:
        return 5.0
    if s.startswith("sim") or "power delivery" in s or "displayport" in s:
        return 8.5
    if s == "não":
        return 3.0
    return 6.5

def gpu_score(value):
    s = str(value).strip()
    sl = s.lower()
    if s in GPU_SCORE:
        return GPU_SCORE[s]
    # Heurística para futuras GPUs dedicadas. A nota continua editável.
    if any(x in sl for x in ["rtx 5090","rtx 5080","rtx 4090"]): return 10.0
    if any(x in sl for x in ["rtx 5070","rtx 4080","rx 7900"]): return 9.5
    if any(x in sl for x in ["rtx 5060","rtx 4070","rx 7800"]): return 9.0
    if any(x in sl for x in ["rtx 5050","rtx 4060","rx 7700"]): return 8.5
    if any(x in sl for x in ["rtx 4050","rtx 3060","rx 7600","arc a"]): return 8.0
    if any(x in sl for x in ["gtx","radeon rx","geforce"]): return 7.5
    return generic_text_score(value)

def semantic_score(criterion, value):
    s = str(value).lower()
    if criterion == "CPU":
        return CPU_SCORE.get(str(value),6.0)
    if criterion == "GPU":
        return gpu_score(value)
    if criterion == "Tipo RAM":
        if "lpddr5" in s or "ddr5" in s: return 9.0
        if "lpddr4" in s: return 7.0
        if "ddr4" in s: return 6.0
    if criterion == "Dual-channel de fábrica":
        return 9.0 if s.startswith("sim") else 3.0
    if criterion == "Expansão de RAM":
        if s.startswith("não"): return 2.0
        if "64gb" in s: return 10.0
        if "32gb" in s: return 9.5
        if "sim" in s: return 8.0
        if "limit" in s: return 5.0
    if criterion == "Tipo/interface SSD":
        if "gen4" in s or "4.0" in s: return 9.0
        if "nvme" in s: return 7.5
    if criterion == "Resolução":
        if any(x in s for x in ["2560","2880","3200","3840"]): return 10.0
        if "1920×1200" in s or "1920x1200" in s: return 9.0
        if "1920×1080" in s or "1920x1080" in s: return 7.0
    if criterion == "Proporção":
        if "16:10" in s or "3:2" in s: return 9.0
        if "16:9" in s: return 6.0
    if criterion == "Painel":
        if "oled" in s: return 10.0
        if "mini" in s and "led" in s: return 9.5
        if "ips" in s and "tn" not in s: return 9.0
        if "wva" in s: return 7.5
        if "tn" in s: return 4.5
    if criterion == "Cobertura de cores":
        if "100%" in s: return 10.0
        if "62,5" in s or "62.5" in s: return 7.0
        if "45%" in s: return 6.0
    if criterion == "Webcam":
        if "1080" in s or "fhd" in s: return 9.0
        if "720" in s or "hd" in s: return 6.0
    if criterion == "Wi‑Fi":
        if "wi-fi 7" in s or "wifi 7" in s: return 10.0
        if "6e" in s: return 9.5
        if "wi‑fi 6" in s or "wi-fi 6" in s or "wifi 6" in s: return 8.5
        if "wi‑fi 5" in s or "wi-fi 5" in s or "wifi 5" in s: return 6.0
    if criterion == "Thunderbolt / USB4":
        if "thunderbolt 5" in s: return 10.0
        if "thunderbolt 4" in s or "usb4" in s: return 9.5
        if s == "não": return 3.0
    if criterion in {"USB‑C com vídeo","USB‑C com carregamento"}:
        return 9.0 if s.startswith("sim") or "displayport" in s or "power delivery" in s else 3.0
    if criterion == "Material / construção":
        if "metá" in s or "alum" in s: return 8.5
        if "plástico" in s: return 6.0
    return generic_text_score(value)

def build_initial_scores(frame):
    models = frame[MODEL_COL].astype(str).tolist()
    out = pd.DataFrame(index=models,columns=IMPORTANT_CRITERIA,dtype=float)
    for c in IMPORTANT_CRITERIA:
        if c in NUMERIC_FIELDS:
            out[c] = numeric_scores(frame[c],c in LOWER_BETTER).values
        else:
            out[c] = frame[c].map(lambda v:semantic_score(c,v)).values
    return out.clip(0,10).round(1)

def reconcile_scores(reset_model=None):
    frame = current_df()
    fresh = build_initial_scores(frame)
    old = st.session_state.get("scores")
    if old is not None:
        for model in fresh.index:
            if model == reset_model or model not in old.index:
                continue
            for c in IMPORTANT_CRITERIA:
                if c in old.columns:
                    fresh.loc[model,c] = old.loc[model,c]
    st.session_state.scores = fresh

def parse_value(col,value):
    value = value.strip()
    if value == "":
        return "N/D"
    if col in NUMERIC_FIELDS:
        cleaned = value.replace("R$","").replace(".","").replace(",",".").strip() if col=="Preço atual (R$)" else value.replace(",",".")
        try:
            number = float(cleaned)
            return int(number) if number.is_integer() else number
        except ValueError:
            return value
    return value

def data_coverage(row):
    relevant = [c for c in IMPORTANT_CRITERIA if c != "Preço atual (R$)"]
    known = 0
    for c in relevant:
        val = str(row.get(c,"N/D")).strip().lower()
        if val not in UNKNOWN_VALUES and "não determin" not in val:
            known += 1
    return round(100*known/len(relevant))

if "inventory" not in st.session_state:
    st.session_state.inventory = [normalize_row(dict(x)) for x in NOTEBOOKS]
if "weights" not in st.session_state:
    st.session_state.weights = DEFAULT_WEIGHTS.copy()
if "scores" not in st.session_state:
    st.session_state.scores = build_initial_scores(current_df())
if "requirements" not in st.session_state:
    st.session_state.requirements = {"max_price":0.0,"min_ram":0,"min_ssd":0,"max_weight":0.0,"usb_c_charge":False}
if "custom_presets" not in st.session_state:
    st.session_state.custom_presets = {}

def models():
    return current_df()[MODEL_COL].astype(str).tolist()

def requirement_status(row):
    req = st.session_state.requirements
    fails = []
    def num(col):
        return pd.to_numeric(pd.Series([row.get(col)]),errors="coerce").iloc[0]
    price,ram,ssd,weight = num("Preço atual (R$)"),num("RAM instalada (GB)"),num("SSD instalado (GB)"),num("Peso (kg)")
    if req["max_price"] > 0 and pd.notna(price) and price > req["max_price"]: fails.append("preço")
    if req["max_price"] > 0 and pd.isna(price): fails.append("preço não informado")
    if req["min_ram"] > 0 and (pd.isna(ram) or ram < req["min_ram"]): fails.append("RAM")
    if req["min_ssd"] > 0 and (pd.isna(ssd) or ssd < req["min_ssd"]): fails.append("SSD")
    if req["max_weight"] > 0 and (pd.isna(weight) or weight > req["max_weight"]): fails.append("peso")
    if req["usb_c_charge"] and not str(row.get("USB‑C com carregamento","")).lower().startswith("sim"): fails.append("USB‑C com carga")
    return ("Atende" if not fails else "Não atende",", ".join(fails))

def ranking(selected_models=None):
    frame = current_df()
    available = frame[MODEL_COL].astype(str).tolist()
    score_df = st.session_state.scores.reindex(available)
    weights = pd.Series(st.session_state.weights,dtype=float)
    active = weights[weights > 0]
    if active.empty:
        total = pd.Series(0.0,index=available)
    else:
        total = score_df[active.index].mul(active,axis=1).sum(axis=1)/active.sum()
    rows=[]
    indexed=frame.set_index(MODEL_COL)
    for model in available:
        status,reason=requirement_status(indexed.loc[model])
        rows.append({
            "Notebook":model,
            "Pontuação":float(total.loc[model]),
            "Nota / 100":round(float(total.loc[model])*10,1),
            "Requisitos":status,
            "Pendências":reason,
            "Cobertura dos dados":f"{data_coverage(indexed.loc[model])}%"
        })
    result=pd.DataFrame(rows)
    if selected_models is not None:
        result=result[result["Notebook"].isin(selected_models)]
    result["_ok"]=result["Requisitos"].eq("Atende").astype(int)
    return result.sort_values(["_ok","Pontuação"],ascending=[False,False]).drop(columns="_ok").reset_index(drop=True)

def notebook_summary(row):
    known = {
        "Galaxy Book4 15,6” — i5-1335U / 8GB / 512GB": SUMMARY["Samsung Galaxy Book4"],
        "Aspire 16 A16-71M-55H0 — Ultra 5 115U / 16GB / 512GB": SUMMARY["Acer Aspire 16"],
        "ThinkPad E14 (Gen 1) — i7-10510U / 8GB / 512GB": SUMMARY["Lenovo ThinkPad E14"],
        "Vivobook 16 X1605VA-MB763W — i7-1355U / 16GB / 512GB": SUMMARY["ASUS Vivobook 16"],
        "200 G2i 16” — Core 5 120U / 8GB / 512GB": SUMMARY["HP 200 G2i"],
        "Dell 15 DC15-I51334U-A50 — i5-1334U / 8GB / 512GB": SUMMARY["Dell A50"],
        "Dell 15 DC15-I51334U-M80 — i5-1334U / 16GB / 1TB": SUMMARY["Dell M80"],
    }
    name=str(row.get(MODEL_COL,""))
    if name in known: return known[name]
    hi=str(row.get("Destaques objetivos","")).strip()
    lo=str(row.get("Limitações / ressalvas","")).strip()
    if hi not in {"","N/D"} and lo not in {"","N/D"}: return f"{hi}. Atenção: {lo}"
    return hi if hi not in {"","N/D"} else "Sem resumo cadastrado."

# ---------------------------------------------------------------------
# Navegação
# ---------------------------------------------------------------------
PAGES = {
    "inicio":"Início",
    "comparativo":"Comparativo lado a lado",
    "pesos":"Pesos",
    "notas":"Notas",
    "ranking":"Ranking",
    "itens":"Itens cadastrados",
    "resumo":"Resumo",
}
PAGE_ICONS = {
    "inicio":"🏠","comparativo":"↔️","pesos":"⚖️","notas":"🎚️",
    "ranking":"🏆","itens":"🗂️","resumo":"📝"
}

query_page = st.query_params.get("page","inicio")
if isinstance(query_page,list): query_page=query_page[0]
if query_page not in PAGES: query_page="inicio"

st.markdown("""
<style>
/* Base */
.block-container {max-width: 1440px; padding-top: 1.3rem; padding-bottom: 3rem;}
[data-testid="stHeaderActionElements"] {display:none !important;}
h1 a, h2 a, h3 a, h4 a {display:none !important;}
h1 {font-size:2.05rem !important; margin-bottom:.15rem !important;}
h2 {font-size:1.45rem !important; margin-top:.7rem !important;}
h3 {font-size:1.05rem !important;}
p, label, div {letter-spacing:-0.005em;}

/* Sidebar */
[data-testid="stSidebar"] {border-right:1px solid rgba(128,128,128,.14);}
[data-testid="stSidebar"] [role="radiogroup"] label {
  border-radius:10px; padding:.25rem .45rem; margin-bottom:.1rem;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
  background:rgba(49,87,213,.07);
}

/* Containers / cards */
[data-testid="stVerticalBlockBorderWrapper"] {
  border-radius:16px !important;
  border-color:rgba(120,130,150,.22) !important;
  box-shadow:0 1px 2px rgba(15,23,42,.025);
}
.feature-card {
  min-height:88px;
}
.muted {color:#697386; font-size:.93rem; line-height:1.45;}
.eyebrow {font-size:.78rem; text-transform:uppercase; letter-spacing:.08em; font-weight:700; color:#667085;}
.section-lead {font-size:1.02rem; color:#667085; max-width:860px; margin-bottom:1rem;}

/* Metrics */
[data-testid="stMetric"] {
  background:rgba(128,128,128,.045);
  border:1px solid rgba(120,130,150,.16);
  padding:14px 16px;
  border-radius:14px;
}
[data-testid="stMetricLabel"] {font-weight:600; color:#667085;}

/* Buttons */
.stButton > button, .stDownloadButton > button {
  border-radius:10px;
  min-height:2.55rem;
  font-weight:600;
}
.stButton > button[kind="primary"] {box-shadow:0 2px 8px rgba(49,87,213,.18);}

/* Dataframes */
[data-testid="stDataFrame"] {
  border:1px solid rgba(120,130,150,.18);
  border-radius:12px;
  overflow:hidden;
}

/* Tabs */
button[data-baseweb="tab"] {font-weight:600;}
</style>
""",unsafe_allow_html=True)

st.title("Nota da Lu")
st.caption("Compare notebooks com critérios explícitos, requisitos mínimos e um ranking que você controla.")

all_models=models()

with st.sidebar:
    nav_options=list(PAGES.keys())
    page=st.radio(
        "Navegação",
        nav_options,
        index=nav_options.index(query_page),
        format_func=lambda p:f"{PAGE_ICONS[p]}  {PAGES[p]}",
        label_visibility="collapsed"
    )
    st.divider()
    st.subheader("Perfil de compra")
    available_presets={**PRESETS, **st.session_state.custom_presets}
    preset=st.selectbox("Preset de pesos",list(available_presets))
    if st.button("Aplicar preset",use_container_width=True):
        st.session_state.weights=available_presets[preset].copy()
        st.rerun()
    st.divider()
    selected=st.multiselect("Itens considerados",all_models,default=all_models)
    with st.expander("Requisitos mínimos"):
        st.caption("Requisitos eliminatórios vêm antes da pontuação.")
        req=st.session_state.requirements
        req["max_price"]=st.number_input("Preço máximo (R$)",min_value=0.0,value=float(req["max_price"]),step=100.0)
        req["min_ram"]=st.number_input("RAM mínima (GB)",min_value=0,value=int(req["min_ram"]),step=4)
        req["min_ssd"]=st.number_input("SSD mínimo (GB)",min_value=0,value=int(req["min_ssd"]),step=128)
        req["max_weight"]=st.number_input("Peso máximo (kg)",min_value=0.0,value=float(req["max_weight"]),step=0.1)
        req["usb_c_charge"]=st.checkbox("Exigir USB‑C com carregamento",value=bool(req["usb_c_charge"]))
        st.session_state.requirements=req
    st.caption(f"{len(st.session_state.inventory)} notebook(s) cadastrado(s).")

# ---------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------
if page=="inicio":
    st.subheader("Escolha como quer começar")
    st.markdown('<div class="section-lead">A ferramenta separa três coisas que costumam ser misturadas: <b>o que o notebook tem</b>, <b>o quanto isso importa para você</b> e <b>quanto aquela configuração merece de nota</b>.</div>',unsafe_allow_html=True)
    cards=[
        ("comparativo","↔️","Comparar lado a lado","Veja até 10 equipamentos juntos, filtre por grupo e esconda tudo que for igual."),
        ("pesos","⚖️","Definir o que importa","Diga quais critérios têm peso real na sua compra. Preço pode entrar no cálculo de valor."),
        ("notas","🎚️","Revisar as notas","Confira a spec que originou cada nota e ajuste qualquer avaliação com a qual não concorde."),
        ("ranking","🏆","Ver o ranking","Veja pontuação ponderada, requisitos mínimos e cobertura dos dados de cada opção."),
        ("itens","🗂️","Gerenciar equipamentos","Cadastre, edite ou remova modelos e preencha todas as especificações."),
        ("resumo","📝","Ler o resumo","Faça uma leitura rápida dos principais pontos fortes, limitações e dados essenciais."),
    ]
    cols=st.columns(2,gap="medium")
    for i,(slug,icon,title,body) in enumerate(cards):
        with cols[i%2]:
            with st.container(border=True):
                st.markdown(f"### {icon} {title}")
                st.markdown(f'<div class="muted">{body}</div>',unsafe_allow_html=True)
                if st.button("Abrir",key=f"home_{slug}",use_container_width=True):
                    st.query_params["page"]=slug
                    st.rerun()
    a,b,c,d=st.columns(4)
    a.metric("Equipamentos",len(all_models))
    b.metric("Specs por item",len(SPEC_COLUMNS))
    c.metric("Critérios pontuados",len(IMPORTANT_CRITERIA))
    d.metric("Critérios eliminatórios",5)
    st.info("Fluxo recomendado: **Comparativo → Requisitos mínimos → Pesos → Notas → Ranking**. Assim o ranking é consequência da decisão, não o ponto de partida.")

elif page=="comparativo":
    st.subheader("Comparativo lado a lado")
    compare=st.multiselect("Escolha até 10 itens",all_models,default=all_models[:min(4,len(all_models))],max_selections=10,key="compare_models")
    c1,c2=st.columns([2,1])
    with c1:
        group3=st.selectbox("Grupo de especificações",["Todos"]+list(GROUPS),key="spec_group")
    with c2:
        only_diff=st.toggle("Mostrar apenas diferenças",value=True)
    if compare:
        frame=current_df()
        full=frame[frame[MODEL_COL].isin(compare)].set_index(MODEL_COL).T
        if group3!="Todos":
            wanted=[c for c in GROUPS[group3] if c!=MODEL_COL]
            full=full.loc[[c for c in wanted if c in full.index]]
        if only_diff and len(compare)>1:
            normalized=full.astype(str).apply(lambda col:col.str.strip())
            full=full[normalized.nunique(axis=1,dropna=False)>1]
        st.dataframe(full,use_container_width=True,height=720)
        st.download_button("Baixar comparação em CSV",full.to_csv().encode("utf-8-sig"),"comparativo_lado_a_lado.csv","text/csv")
    else:
        st.info("Escolha pelo menos um item.")

elif page=="pesos":
    st.subheader("Pesos dos critérios")
    st.caption("0 ignora um critério; 10 dá importância máxima. Requisitos obrigatórios devem ser configurados na barra lateral, não como peso.")
    group=st.selectbox("Grupo",["Todos"]+list(IMPORTANT_GROUPS),key="weight_group")
    weight_cols=IMPORTANT_CRITERIA if group=="Todos" else IMPORTANT_GROUPS[group]
    weight_df=pd.DataFrame({"Critério":weight_cols,"Peso":[st.session_state.weights[c] for c in weight_cols]})
    edited=st.data_editor(weight_df,hide_index=True,use_container_width=True,
        column_config={"Peso":st.column_config.NumberColumn(min_value=0,max_value=10,step=1,format="%d")},
        disabled=["Critério"],key=f"weight_editor_{group}")
    if st.button("Aplicar pesos",type="primary"):
        for _,r in edited.iterrows(): st.session_state.weights[r["Critério"]]=float(r["Peso"])
        st.rerun()

    st.divider()
    st.markdown("### Presets personalizados")
    st.caption("Aplique um preset-base, ajuste os pesos acima e salve a combinação com outro nome.")
    p1,p2=st.columns([2,1])
    with p1:
        preset_name=st.text_input("Nome do novo preset",placeholder="Ex.: Trabalho remoto da Lu")
    with p2:
        st.write("")
        st.write("")
        save_preset=st.button("Salvar preset atual",use_container_width=True)
    if save_preset:
        clean_name=preset_name.strip()
        if not clean_name:
            st.error("Dê um nome ao preset.")
        elif clean_name in PRESETS:
            st.error("Esse nome é reservado para um preset-base do sistema.")
        else:
            st.session_state.custom_presets[clean_name]=st.session_state.weights.copy()
            st.success(f'Preset "{clean_name}" salvo para esta sessão.')
            st.rerun()

    if st.session_state.custom_presets:
        st.markdown("**Seus presets**")
        cp=st.selectbox("Preset personalizado",list(st.session_state.custom_presets),key="custom_preset_manage")
        cpa,cpb=st.columns(2)
        if cpa.button("Aplicar",key="apply_custom",use_container_width=True):
            st.session_state.weights=st.session_state.custom_presets[cp].copy()
            st.rerun()
        if cpb.button("Excluir",key="delete_custom",use_container_width=True):
            del st.session_state.custom_presets[cp]
            st.rerun()

elif page=="notas":
    st.subheader("Notas das características")
    st.caption("A nota sempre aparece junto da especificação real que está sendo avaliada.")
    score_group=st.selectbox("Grupo",list(IMPORTANT_GROUPS),key="score_group")
    criterion=st.selectbox("Critério",IMPORTANT_GROUPS[score_group],key="score_criterion")
    frame=current_df().set_index(MODEL_COL)
    rows=[]
    for model in selected:
        if model in frame.index:
            rows.append({"Notebook":model,"Spec":frame.loc[model,criterion],"Nota":float(st.session_state.scores.loc[model,criterion])})
    score_edit=pd.DataFrame(rows)
    if score_edit.empty:
        st.warning("Selecione pelo menos um item na barra lateral.")
    else:
        edited_scores=st.data_editor(score_edit,hide_index=True,use_container_width=True,
            column_config={"Spec":st.column_config.TextColumn(width="large"),"Nota":st.column_config.NumberColumn(min_value=0.0,max_value=10.0,step=.1,format="%.1f")},
            disabled=["Notebook","Spec"],key=f"score_editor_{criterion}")
        if st.button("Aplicar notas",type="primary"):
            for _,r in edited_scores.iterrows(): st.session_state.scores.loc[r["Notebook"],criterion]=float(r["Nota"])
            st.rerun()
        st.caption("Notas automáticas são apenas um ponto de partida. Para CPUs/GPUs novas ou incomuns, revise a nota manualmente.")

elif page=="ranking":
    st.subheader("Ranking personalizado")
    rank=ranking(selected)
    if rank.empty:
        st.warning("Selecione pelo menos um item na barra lateral.")
    else:
        eligible=rank[rank["Requisitos"]=="Atende"]
        if len(eligible):
            winner=eligible.iloc[0]
            c1,c2,c3,c4=st.columns(4)
            c1.metric("Melhor entre os elegíveis",winner["Notebook"].split(" — ")[0])
            c2.metric("Nota",f'{winner["Nota / 100"]:.1f}/100')
            c3.metric("Critérios ativos",sum(v>0 for v in st.session_state.weights.values()))
            c4.metric("Elegíveis",f"{len(eligible)}/{len(rank)}")
        else:
            st.warning("Nenhum item atende aos requisitos mínimos atuais.")
        plot=rank.copy()
        fig=px.bar(plot.sort_values("Pontuação"),x="Nota / 100",y="Notebook",orientation="h",text="Nota / 100",color="Requisitos",range_x=[0,100])
        fig.update_layout(height=max(360,58*len(plot)),margin=dict(l=10,r=20,t=20,b=10),xaxis_title="Pontuação ponderada",yaxis_title="")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(rank[["Notebook","Nota / 100","Requisitos","Pendências","Cobertura dos dados"]],hide_index=True,use_container_width=True)
        if any(str(x)=="5.0" for x in []): pass
        if current_df()["Preço atual (R$)"].astype(str).str.lower().isin(UNKNOWN_VALUES).all():
            st.info("Nenhum preço foi cadastrado ainda. O peso de preço está ativo, mas todos recebem nota neutra nesse critério; cadastre os preços para o ranking refletir custo-benefício.")
        st.download_button("Baixar ranking em CSV",rank.to_csv(index=False).encode("utf-8-sig"),"ranking_notebooks.csv","text/csv")

elif page=="itens":
    st.subheader("Gestão de itens cadastrados")
    manage_tabs=st.tabs(["Cadastrados","Adicionar / editar","Importar / exportar"])
    with manage_tabs[0]:
        frame=current_df()
        overview_cols=["Marca",MODEL_COL,"Preço atual (R$)","CPU","GPU","RAM instalada (GB)","SSD instalado (GB)","Tela (pol.)","Peso (kg)"]
        st.dataframe(frame[overview_cols],hide_index=True,use_container_width=True)
        remove_item=st.selectbox("Remover item",["— selecione —"]+all_models,key="remove_item")
        confirm=st.checkbox("Confirmo a remoção do item selecionado.",key="confirm_remove")
        if st.button("Remover",disabled=remove_item=="— selecione —" or not confirm):
            st.session_state.inventory=[r for r in st.session_state.inventory if str(r.get(MODEL_COL))!=remove_item]
            reconcile_scores()
            st.rerun()
    with manage_tabs[1]:
        edit_choice=st.selectbox("O que deseja editar?",["➕ Novo item"]+all_models,key="edit_choice")
        existing=None if edit_choice=="➕ Novo item" else next((r for r in st.session_state.inventory if str(r.get(MODEL_COL))==edit_choice),None)
        base=normalize_row(existing) if existing else {c:"" for c in SPEC_COLUMNS}
        st.caption("GPU é o campo usado no ranking. Em novos itens, se ele ficar vazio, o sistema usa GPU dedicada quando houver; caso contrário, usa a integrada.")
        with st.form("item_form"):
            values={}
            for group_name,cols in GROUPS.items():
                with st.expander(group_name,expanded=group_name in {"Identificação","Compra"}):
                    for col in cols:
                        default=base.get(col,"")
                        values[col]=st.text_input(col,value="" if str(default)=="N/D" and existing is None else str(default),key=f"field_{edit_choice}_{col}")
            save=st.form_submit_button("Salvar item",type="primary",use_container_width=True)
        if save:
            parsed={c:parse_value(c,values.get(c,"")) for c in SPEC_COLUMNS}
            if str(parsed.get("GPU","")).strip().lower() in UNKNOWN_VALUES:
                parsed["GPU"]=resolved_gpu(parsed)
            new_name=str(parsed.get(MODEL_COL,"")).strip()
            if new_name in {"","N/D"}:
                st.error("Preencha **Modelo / configuração**.")
            else:
                duplicate=any(str(r.get(MODEL_COL))==new_name for r in st.session_state.inventory if r is not existing)
                if duplicate:
                    st.error("Já existe um item com esse mesmo nome/modelo.")
                else:
                    old_name=str(existing.get(MODEL_COL)) if existing else None
                    if existing:
                        st.session_state.inventory[st.session_state.inventory.index(existing)]=parsed
                    else:
                        st.session_state.inventory.append(parsed)
                    if old_name and old_name!=new_name and old_name in st.session_state.scores.index:
                        st.session_state.scores=st.session_state.scores.drop(index=old_name)
                    reconcile_scores(reset_model=new_name)
                    st.rerun()
    with manage_tabs[2]:
        export_json=json.dumps(st.session_state.inventory,ensure_ascii=False,indent=2)
        st.download_button("Baixar backup JSON",export_json.encode("utf-8"),"notebooks_backup.json","application/json",use_container_width=True)
        uploaded=st.file_uploader("Importar backup JSON",type=["json"])
        if uploaded is not None:
            try:
                imported=json.load(uploaded)
                if not isinstance(imported,list): raise ValueError("O JSON precisa conter uma lista de itens.")
                normalized=[normalize_row(item) for item in imported if isinstance(item,dict)]
                if st.button("Substituir cadastro pelo arquivo importado",type="primary"):
                    st.session_state.inventory=normalized
                    st.session_state.scores=build_initial_scores(current_df())
                    st.rerun()
            except Exception as exc:
                st.error(f"Não foi possível ler o arquivo: {exc}")
        st.warning("Cadastros feitos pela interface ficam na sessão atual. Use o backup JSON para preservá-los entre reinicializações/redeploys do Railway.")

elif page=="resumo":
    st.subheader("Resumo dos equipamentos")
    frame=current_df()
    for _,row in frame.iterrows():
        with st.container(border=True):
            st.markdown(f"### {row[MODEL_COL]}")
            st.write(notebook_summary(row))
            c1,c2,c3,c4,c5=st.columns(5)
            c1.metric("CPU",str(row["CPU"]))
            c2.metric("GPU",str(row["GPU"]))
            c3.metric("RAM",f'{row["RAM instalada (GB)"]} GB')
            c4.metric("Bateria",f'{row["Bateria (Wh)"]} Wh')
            c5.metric("Peso",f'{row["Peso (kg)"]} kg')
            price=row.get("Preço atual (R$)","N/D")
            if str(price).lower() not in UNKNOWN_VALUES:
                st.caption(f"Preço cadastrado: R$ {float(price):,.2f}".replace(",", "X").replace(".", ",").replace("X","."))
    st.divider()
    st.markdown("**Como interpretar o sistema**")
    st.write("1. Requisitos mínimos eliminam opções incompatíveis. 2. Pesos representam suas prioridades. 3. Notas representam a qualidade de cada spec. 4. A cobertura dos dados mostra quanto da comparação está apoiada em informações conhecidas. 5. O ranking organiza a decisão, mas não substitui preço atualizado, garantia, reputação do vendedor e inspeção final do anúncio.")
