import pygame
import random
import math
import sys

# Inizializzazione Pygame
pygame.init()

# Finestra di gioco
WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("COSMO-DEX // Quasicrystal Interceptor")

# Palette colori in stile terminale quantistico / dark mode
BG_COLOR = (14, 17, 23)      # #0e1117 (lo sfondo del tuo progetto Streamlit)
PANEL_COLOR = (22, 27, 34)   # #161b22
TEXT_COLOR = (240, 246, 252)
ACCENT_CYAN = (0, 212, 255)
GOLDEN = (255, 215, 0)       # Richiamo alla costante aurea PHI
PHASON_RED = (255, 75, 75)
GRID_COLOR = (33, 38, 45)

clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier New", 24, bold=True)
small_font = pygame.font.SysFont("Courier New", 16)

# Stato del Giocatore (Satellite Scanner)
player_x = WIDTH // 2
player_y = HEIGHT - 100
player_size = 30
player_speed = 8

# Entità di gioco
nodes = []      # Nodi aurei da raccogliere (+ Coerenza)
glitches = []   # Fluttuazioni fasoniche instabili / ostacoli (- Coerenza)
lasers = []     # Colpi energetici

coherence = 100.0  # Barra di integrità del sistema
score = 0
phase_angle = 0.0

running = True
game_over = False

while running:
    screen.fill(BG_COLOR)
    
    # 1. Gestione Eventi
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                # Spara raggio di stabilizzazione fasonica
                lasers.append([player_x, player_y])
            elif event.key == pygame.K_r and game_over:
                # Restart
                coherence = 100.0
                score = 0
                nodes.clear()
                glitches.clear()
                lasers.clear()
                game_over = False

    if not game_over:
        # Controlli di movimento (Frecce o WASD)
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player_x > 40:
            player_x -= player_speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player_x < WIDTH - 40:
            player_x += player_speed
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and player_y > 100:
            player_y -= player_speed
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and player_y < HEIGHT - 50:
            player_y += player_speed

        # Aggiornamento fase fasonica di sfondo
        phase_angle += 0.05

        # 2. Spawn Entità (Nodi Quasicristalli e Glitch Fasonici)
        if random.random() < 0.03:
            nodes.append([random.randint(50, WIDTH - 50), -20, random.uniform(1.5, 3.0)])
        if random.random() < 0.025:
            glitches.append([random.randint(50, WIDTH - 50), -20, random.uniform(2.0, 4.5)])

        # 3. Disegno e Aggiornamento Griglia Aperiodica di Sfondo
        for x in range(0, WIDTH, 60):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 60):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y), 1)

        # 4. Gestione Laser
        for laser in lasers[:]:
            laser[1] -= 12
            if laser[1] < 0:
                lasers.remove(laser)
            else:
                pygame.draw.rect(screen, ACCENT_CYAN, (laser[0] - 2, laser[1], 4, 15))

        # 5. Gestione Nodi Aurei (Raccolta)
        for node in nodes[:]:
            node[1] += node[2]
            if node[1] > HEIGHT:
                nodes.remove(node)
            else:
                # Disegna Nodo aperiodico (Cerchio Dorato)
                pygame.draw.circle(screen, GOLDEN, (int(node[0]), int(node[1])), 8)
                
                # Collisione Giocatore - Nodo
                dist = math.hypot(player_x - node[0], player_y - node[1])
                if dist < player_size + 8:
                    nodes.remove(node)
                    score += 50
                    coherence = min(100.0, coherence + 5.0)

        # 6. Gestione Glitch Fasonici (Ostacoli)
        for glitch in glitches[:]:
            glitch[1] += glitch[2]
            if glitch[1] > HEIGHT:
                glitches.remove(glitch)
            else:
                # Disegna Glitch (Rombo Rosso Instabile)
                pts = [
                    (glitch[0], glitch[1] - 12),
                    (glitch[0] + 12, glitch[1]),
                    (glitch[0], glitch[1] + 12),
                    (glitch[0] - 12, glitch[1])
                ]
                pygame.draw.polygon(screen, PHASON_RED, pts)

                # Collisione Laser - Glitch (Distrugge il glitch)
                for laser in lasers[:]:
                    if math.hypot(laser[0] - glitch[0], laser[1] - glitch[1]) < 18:
                        if glitch in glitches: glitches.remove(glitch)
                        if laser in lasers: lasers.remove(laser)
                        score += 20
                        break

                # Collisione Giocatore - Glitch (Danno alla coerenza)
                if math.hypot(player_x - glitch[0], player_y - glitch[1]) < player_size + 10:
                    glitches.remove(glitch)
                    coherence -= 20.0
                    if coherence <= 0:
                        coherence = 0.0
                        game_over = True

        # 7. Disegno Giocatore (Navicella Cosmo-Dex a forma di sonda geometrica)
        ship_pts = [
            (player_x, player_y - player_size),
            (player_x - player_size // 1.5, player_y + player_size),
            (player_x, player_y + player_size // 2),
            (player_x + player_size // 1.5, player_y + player_size)
        ]
        pygame.draw.polygon(screen, ACCENT_CYAN, ship_pts)
        
        # Effetto scia fasonica dietro la navicella
        pygame.draw.circle(screen, ACCENT_CYAN, (int(player_x), int(player_y + player_size)), int(4 + math.sin(phase_angle)*2))

    # 8. Interfaccia HUD superiore in stile Dashboard Streamlit
    pygame.draw.rect(screen, PANEL_COLOR, (0, 0, WIDTH, 70))
    pygame.draw.line(screen, ACCENT_CYAN, (0, 70), (WIDTH, 70), 2)

    score_txt = font.render(f"SCORE: {score}", True, TEXT_COLOR)
    coherence_txt = font.render(f"COHERENCE: {int(coherence)}%", True, GOLDEN if coherence > 30 else PHASON_RED)
    
    screen.blit(score_txt, (30, 20))
    screen.blit(coherence_txt, (300, 20))

    # Barra della coerenza visiva
    pygame.draw.rect(screen, GRID_COLOR, (650, 25, 200, 20), border_radius=4)
    pygame.draw.rect(screen, GOLDEN if coherence > 30 else PHASON_RED, (650, 25, int(2 * coherence), 20), border_radius=4)

    # Schermata Game Over
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((14, 17, 23, 220))
        screen.blit(overlay, (0, 0))
        
        go_txt = font.render("SYSTEM FAILURE // COHERENCE COLLAPSED", True, PHASON_RED)
        restart_txt = small_font.render("Premi [R] per ricaricare il reticolo o [ESC] per uscire", True, TEXT_COLOR)
        
        screen.blit(go_txt, (WIDTH // 2 - go_txt.get_width() // 2, HEIGHT // 2 - 30))
        screen.blit(restart_txt, (WIDTH // 2 - restart_txt.get_width() // 2, HEIGHT // 2 + 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
