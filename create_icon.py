try:
    from PIL import Image, ImageDraw, ImageFont
    
    # Crea un'immagine 512x512 con sfondo scuro a tema COSMODEX
    size = (512, 512)
    image = Image.new("RGB", size, color="#05050a")
    draw = ImageDraw.Draw(image)
    
    # Disegna un cerchio o un elemento geometrico neon (stile aperiodico)
    draw.ellipse([100, 100, 412, 412], outline="#00ffcc", width=12)
    draw.rectangle([180, 180, 332, 332], outline="#ffaa00", width=8)
    
    # Salva l'icona
    image.save("icon-512.png", "PNG")
    print("icon-512.png generata con successo!")

except ImportError:
    # Fallback se la libreria Pillow non è installata: crea un file PNG valido minimale
    # (colore solido 1x1 ingrandito o binario valido)
    print("Libreria Pillow non trovata. Installala con: pip install Pillow")
