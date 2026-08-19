import random
import math
import json
import os

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse, Line, Triangle, Mesh
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

# Tamanho padrão simulação celular
Window.size = (400, 700)

ARQUIVO_DADOS = "dados_jogo.json"

# Funções de Placar
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r") as f:
                return json.load(f)
        except:
            pass
    return {
        "top3": [{"nome": "AAA", "pontos": 0}, {"nome": "BBB", "pontos": 0}, {"nome": "CCC", "pontos": 0}],
        "ultimos": []
    }

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w") as f:
        json.dump(dados, f, indent=4)

def registrar_pontuacao(nome, pontos):
    dados = carregar_dados()
    dados["ultimos"].insert(0, {"nome": nome, "pontos": pontos})
    dados["ultimos"] = dados["ultimos"][:7]
    dados["top3"].append({"nome": nome, "pontos": pontos})
    dados["top3"] = sorted(dados["top3"], key=lambda x: x["pontos"], reverse=True)[:3]
    salvar_dados(dados)

# Botão Estilizado Synthwave com Bordas Neon
class BotaoSynthwave(Button):
    def __init__(self, cor_borda=(0, 1, 1, 1), **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)  # Remove o cinza padrão do Kivy
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.font_size = '15sp'
        self.cor_borda = cor_borda
        self.bind(pos=self.atualizar_visual, size=self.atualizar_visual)

    def atualizar_visual(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Fundo translúcido escuro
            Color(0.08, 0.02, 0.15, 0.85)
            Rectangle(pos=self.pos, size=self.size)
            # Borda com brilho Synthwave
            Color(*self.cor_borda)
            Line(rect=(self.pos[0], self.pos[1], self.size[0], self.size[1]), width=1.5)

# Widget do Jogo Principal
class SpaceDefenderApp(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.estado = "MENU"
        self.modo_dificil = False
        
        self.nave_x = 180
        self.nave_y = 120
        self.nave_largura = 40
        self.nave_altura = 35
        
        self.mover_esq = False
        self.mover_dir = False
        
        self.tiros = []
        self.inimigos = []
        self.pontuacao = 0
        self.tempo_inicio = 0
        self.tempo_sobrevivido = 0
        
        self.estrelas = [(random.random(), random.uniform(0.4, 0.95), random.uniform(1.5, 3)) for _ in range(40)]
        self.offset_grade = 0
        
        Clock.schedule_interval(self.atualizar, 1.0 / 60.0)

    def iniciar_partida(self, dificil=False):
        w = self.width if self.width > 0 else 400
        self.nave_x = (w - self.nave_largura) / 2
        self.nave_y = 120
        self.tiros = []
        self.inimigos = []
        
        self.modo_dificil = dificil
        self.quant_base = 5 if dificil else 3
        self.vel_base = 6.0 if dificil else 3.0
        
        self.pontuacao = 0
        self.tempo_sobrevivido = 0
        self.tempo_inicio = Clock.get_time()
        
        self.estado = "JOGANDO"

    def criar_inimigo(self):
        w = self.width if self.width > 0 else 400
        h = self.height if self.height > 0 else 700
        x = random.randint(30, int(w - 50))
        y = h + random.randint(10, 100)
        return {"x": x, "y": y, "w": 32, "h": 32}

    def disparar(self):
        if self.estado == "JOGANDO":
            self.tiros.append({"x": self.nave_x + 18, "y": self.nave_y + 35, "w": 4, "h": 16})

    def atualizar(self, dt):
        self.offset_grade = (self.offset_grade + 1.5) % 25

        if self.estado == "JOGANDO":
            tempo_atual = Clock.get_time()
            self.tempo_sobrevivido = int(tempo_atual - self.tempo_inicio)

            mult = 5 if self.modo_dificil else 1
            vel_atual = self.vel_base + ((self.tempo_sobrevivido // 10) * mult * 0.5)
            quant_desejada = self.quant_base + ((self.tempo_sobrevivido // 12) * mult)

            if self.mover_esq and self.nave_x > 10:
                self.nave_x -= 6
            if self.mover_dir and self.nave_x < self.width - self.nave_largura - 10:
                self.nave_x += 6

            while len(self.inimigos) < quant_desejada:
                self.inimigos.append(self.criar_inimigo())

            for tiro in self.tiros[:]:
                tiro["y"] += 12
                if tiro["y"] > self.height:
                    self.tiros.remove(tiro)

            for inimigo in self.inimigos[:]:
                inimigo["y"] -= vel_atual

                for tiro in self.tiros[:]:
                    if (tiro["x"] < inimigo["x"] + inimigo["w"] and tiro["x"] + tiro["w"] > inimigo["x"] and
                        tiro["y"] < inimigo["y"] + inimigo["h"] and tiro["y"] + tiro["h"] > inimigo["y"]):
                        if tiro in self.tiros: self.tiros.remove(tiro)
                        if inimigo in self.inimigos: self.inimigos.remove(inimigo)
                        self.pontuacao += 10 * (2 if self.modo_dificil else 1)
                        break

                if (self.nave_x < inimigo["x"] + inimigo["w"] and self.nave_x + self.nave_largura > inimigo["x"] and
                    self.nave_y < inimigo["y"] + inimigo["h"] and self.nave_y + self.nave_altura > inimigo["y"]):
                    self.estado = "GAME_OVER"
                    App.get_running_app().exibir_input_game_over()

                if inimigo["y"] < -40:
                    if inimigo in self.inimigos: self.inimigos.remove(inimigo)

        self.desenhar_cena()

    def desenhar_cena(self):
        self.canvas.clear()
        w, h = self.width, self.height
        if w == 0 or h == 0:
            return

        with self.canvas:
            # Fundo Synthwave Sunset
            Color(0.05, 0.01, 0.1, 1)
            Rectangle(pos=(0, 0), size=(w, h))

            Color(0, 1, 1, 0.8)
            for ex, ey, es in self.estrelas:
                Ellipse(pos=(ex * w, ey * h), size=(es, es))

            centro_x = w / 2
            centro_y = h * 0.58
            raio = min(w, h) * 0.22
            
            Color(1, 0.8, 0, 1)
            for y_line in range(int(centro_y - raio), int(centro_y + raio), 4):
                if y_line < centro_y and (y_line // 4) % 2 == 0:
                    continue
                dist_y = abs(y_line - centro_y)
                if dist_y < raio:
                    larg_linha = math.sqrt(raio**2 - dist_y**2)
                    Line(points=[centro_x - larg_linha, y_line, centro_x + larg_linha, y_line], width=1.5)

            horizonte_y = h * 0.48
            Color(1, 0, 0.5, 1)
            Line(points=[0, horizonte_y, w, horizonte_y], width=2)

            Color(0.3, 0.05, 0.4, 0.8)
            for y in range(int(horizonte_y), 0, -20):
                pos_y = y - self.offset_grade
                if pos_y > 0:
                    Line(points=[0, pos_y, w, pos_y], width=1)

            for x in range(-int(w), int(w * 2), int(w / 8)):
                Line(points=[centro_x, horizonte_y, x, 0], width=1)

            if self.estado == "JOGANDO":
                nx, ny = self.nave_x, self.nave_y
                nw, nh = self.nave_largura, self.nave_altura

                Color(1, 0, 0.5, 1)
                Triangle(points=[nx + nw/2 - 4, ny - 2, nx + nw/2 + 4, ny - 2, nx + nw/2, ny - 12])

                Color(0, 1, 1, 1)
                Triangle(points=[nx + nw/2, ny + nh, nx, ny, nx + nw/2, ny + 6])
                Triangle(points=[nx + nw/2, ny + nh, nx + nw/2, ny + 6, nx + nw, ny])
                
                Color(1, 1, 1, 1)
                Line(points=[nx + nw/2, ny + nh, nx, ny, nx + nw/2, ny + 6, nx + nw, ny, nx + nw/2, ny + nh], width=1.2)

                for i in self.inimigos:
                    ix, iy = i["x"], i["y"]
                    iw, ih = i["w"], i["h"]
                    cx, cy = ix + iw/2, iy + ih/2
                    
                    Color(1, 0, 0.5, 1)
                    Mesh(vertices=[cx, iy + ih, 0, 0, ix + iw, cy, 0, 0, cx, iy, 0, 0, ix, cy, 0, 0], 
                         indices=[0, 1, 2, 2, 3, 0], mode='triangles')
                    
                    Color(1, 0.8, 0, 1)
                    Line(points=[cx, iy + ih, ix + iw, cy, cx, iy, ix, cy, cx, iy + ih], width=1.5)

                Color(1, 0, 0.5, 1)
                for t in self.tiros:
                    Rectangle(pos=(t["x"], t["y"]), size=(t["w"], t["h"]))

# Aplicação Principal e Gerenciamento de Interface
class JogoApp(App):
    def build(self):
        self.root = FloatLayout()
        
        self.jogo = SpaceDefenderApp(size_hint=(1, 1))
        self.root.add_widget(self.jogo)

        # Monta a Tela do Menu Principal Synthwave
        self.montar_menu_principal()

        # Layout de Controles Virtuais do Jogo (Oculto no Menu)
        self.box_controles = BoxLayout(size_hint=(1, 0.12), pos_hint={'x': 0, 'y': 0}, spacing=10, padding=10)
        btn_esq = BotaoSynthwave(text="< ESQ", cor_borda=(0, 1, 1, 1))
        btn_esq.bind(on_press=lambda x: setattr(self.jogo, 'mover_esq', True))
        btn_esq.bind(on_release=lambda x: setattr(self.jogo, 'mover_esq', False))

        btn_dir = BotaoSynthwave(text="DIR >", cor_borda=(0, 1, 1, 1))
        btn_dir.bind(on_press=lambda x: setattr(self.jogo, 'mover_dir', True))
        btn_dir.bind(on_release=lambda x: setattr(self.jogo, 'mover_dir', False))

        btn_tiro = BotaoSynthwave(text="ATIRAR 🔥", cor_borda=(1, 0, 0.5, 1))
        btn_tiro.bind(on_press=lambda x: self.jogo.disparar())

        self.box_controles.add_widget(btn_esq)
        self.box_controles.add_widget(btn_dir)
        self.box_controles.add_widget(btn_tiro)

        # HUD do Placar
        self.lbl_hud = Label(text="", font_size=16, bold=True, color=(1, 1, 1, 1),
                             size_hint=(None, None), pos_hint={'x': 0.05, 'top': 0.98})
        self.root.add_widget(self.lbl_hud)

        Clock.schedule_interval(self.atualizar_hud, 1.0 / 30.0)
        return self.root

    def montar_menu_principal(self):
        self.box_menu = BoxLayout(orientation='vertical', size_hint=(0.88, 0.68),
                                  pos_hint={'center_x': 0.5, 'center_y': 0.5}, spacing=12, padding=18)
        
        # Painel Fundo Glassmorphism
        self.box_menu.canvas.before.clear()
        with self.box_menu.canvas.before:
            Color(0.04, 0.01, 0.09, 0.92)  # Painel escuro fosco
            Rectangle(pos=self.box_menu.pos, size=self.box_menu.size)
            Color(1, 0, 0.5, 1)  # Borda Rosa Neon
            Line(rect=(self.box_menu.pos[0], self.box_menu.pos[1], self.box_menu.size[0], self.box_menu.size[1]), width=2)

        self.box_menu.bind(pos=self._atualizar_painel_menu, size=self._atualizar_painel_menu)

        lbl_titulo = Label(text="SPACE DEFENDER", font_size='22sp', bold=True, color=(0, 1, 1, 1))
        self.box_menu.add_widget(lbl_titulo)

        btn_normal = BotaoSynthwave(text=">> 1. JOGAR (MODO NORMAL)", cor_borda=(0, 1, 1, 1))
        btn_normal.bind(on_press=lambda x: self.iniciar_jogo(dificil=False))
        self.box_menu.add_widget(btn_normal)

        btn_dificil = BotaoSynthwave(text=">> 2. JOGAR (DIFÍCIL 5X)", cor_borda=(1, 0, 0.5, 1))
        btn_dificil.bind(on_press=lambda x: self.iniciar_jogo(dificil=True))
        self.box_menu.add_widget(btn_dificil)

        btn_placar = BotaoSynthwave(text=">> 3. HISTÓRICO SCORES", cor_borda=(1, 0.8, 0, 1))
        btn_placar.bind(on_press=lambda x: self.exibir_placar())
        self.box_menu.add_widget(btn_placar)

        btn_sair = BotaoSynthwave(text=">> 4. SAIR DO JOGO", cor_borda=(0.6, 0.6, 0.6, 1))
        btn_sair.bind(on_press=lambda x: App.get_running_app().stop())
        self.box_menu.add_widget(btn_sair)

        self.root.add_widget(self.box_menu)

    def _atualizar_painel_menu(self, instance, value):
        self.box_menu.canvas.before.clear()
        with self.box_menu.canvas.before:
            Color(0.04, 0.01, 0.09, 0.92)
            Rectangle(pos=instance.pos, size=instance.size)
            Color(1, 0, 0.5, 1)
            Line(rect=(instance.pos[0], instance.pos[1], instance.size[0], instance.size[1]), width=2)

    def iniciar_jogo(self, dificil):
        if self.box_menu in self.root.children: self.root.remove_widget(self.box_menu)
        if hasattr(self, 'box_placar') and self.box_placar in self.root.children: self.root.remove_widget(self.box_placar)
        if hasattr(self, 'box_go') and self.box_go in self.root.children: self.root.remove_widget(self.box_go)

        self.root.add_widget(self.box_controles)
        self.jogo.iniciar_partida(dificil=dificil)

    def exibir_placar(self):
        if self.box_menu in self.root.children:
            self.root.remove_widget(self.box_menu)

        dados = carregar_dados()
        self.box_placar = BoxLayout(orientation='vertical', size_hint=(0.9, 0.8),
                                    pos_hint={'center_x': 0.5, 'center_y': 0.5}, spacing=6, padding=12)
        
        with self.box_placar.canvas.before:
            Color(0.04, 0.01, 0.09, 0.95)
            Rectangle(pos=self.box_placar.pos, size=self.box_placar.size)
            Color(0, 1, 1, 1)
            Line(rect=(self.box_placar.pos[0], self.box_placar.pos[1], self.box_placar.size[0], self.box_placar.size[1]), width=2)

        self.box_placar.add_widget(Label(text="--- TOP 3 FIXOS ---", font_size='16sp', bold=True, color=(1, 0.8, 0, 1)))
        for idx, item in enumerate(dados["top3"]):
            self.box_placar.add_widget(Label(text=f"{idx+1}º  {item['nome']}  -  {item['pontos']} PTS", font_size='14sp', bold=True, color=(0, 1, 1, 1)))

        self.box_placar.add_widget(Label(text="--- ÚLTIMAS PARTIDAS ---", font_size='16sp', bold=True, color=(1, 0, 0.5, 1)))
        ultimos = dados["ultimos"]
        for idx in range(5):
            if idx < len(ultimos):
                item = ultimos[idx]
                txt = f"{idx+4}º  {item['nome']}  -  {item['pontos']} PTS"
            else:
                txt = f"{idx+4}º  ---  -  0 PTS"
            self.box_placar.add_widget(Label(text=txt, font_size='13sp', color=(0.8, 0.8, 0.8, 1)))

        btn_voltar = BotaoSynthwave(text="VOLTAR AO MENU", cor_borda=(0, 1, 1, 1), size_hint=(1, 0.2))
        btn_voltar.bind(on_press=lambda x: self.voltar_menu())
        self.box_placar.add_widget(btn_voltar)

        self.root.add_widget(self.box_placar)

    def voltar_menu(self):
        if hasattr(self, 'box_placar') and self.box_placar in self.root.children: self.root.remove_widget(self.box_placar)
        if hasattr(self, 'box_go') and self.box_go in self.root.children: self.root.remove_widget(self.box_go)
        if self.box_controles in self.root.children: self.root.remove_widget(self.box_controles)

        self.jogo.estado = "MENU"
        self.root.add_widget(self.box_menu)

    def exibir_input_game_over(self):
        if self.box_controles in self.root.children:
            self.root.remove_widget(self.box_controles)

        self.box_go = BoxLayout(orientation='vertical', size_hint=(0.85, 0.48),
                                pos_hint={'center_x': 0.5, 'center_y': 0.5}, spacing=10, padding=15)
        
        with self.box_go.canvas.before:
            Color(0.04, 0.01, 0.09, 0.95)
            Rectangle(pos=self.box_go.pos, size=self.box_go.size)
            Color(1, 0, 0.5, 1)
            Line(rect=(self.box_go.pos[0], self.box_go.pos[1], self.box_go.size[0], self.box_go.size[1]), width=2)

        self.box_go.add_widget(Label(text="GAME OVER!", font_size='22sp', bold=True, color=(1, 0, 0.5, 1)))
        self.box_go.add_widget(Label(text=f"Pontos: {self.jogo.pontuacao} | Tempo: {self.jogo.tempo_sobrevivido}s", font_size='14sp', bold=True))
        
        self.txt_nome = TextInput(text="AAA", multiline=False, halign="center", font_size='18sp', size_hint=(1, 0.28))
        self.box_go.add_widget(self.txt_nome)

        btn_salvar = BotaoSynthwave(text="SALVAR & MENU", cor_borda=(0, 1, 1, 1), size_hint=(1, 0.28))
        btn_salvar.bind(on_press=self.salvar_e_voltar)
        self.box_go.add_widget(btn_salvar)

        self.root.add_widget(self.box_go)

    def salvar_e_voltar(self, instance):
        nome = self.txt_nome.text.upper()[:3]
        if not nome: nome = "AAA"
        registrar_pontuacao(nome, self.jogo.pontuacao)
        self.voltar_menu()

    def atualizar_hud(self, dt):
        if self.jogo.estado == "JOGANDO":
            mod_txt = " (DIFÍCIL 5X)" if self.jogo.modo_dificil else ""
            self.lbl_hud.text = f"Pontos: {self.jogo.pontuacao}{mod_txt} | Tempo: {self.jogo.tempo_sobrevivido}s"
        else:
            self.lbl_hud.text = ""

if __name__ == "__main__":
    JogoApp().run()