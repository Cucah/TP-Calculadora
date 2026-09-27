import customtkinter as ctk
import os
import json

class win(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        #configs
        self.title("TP Calculadora")
        self.geometry("1000x650")
        self.update()
        
        #icone do bagui
        
        self.iconbitmap(os.path.join(os.path.dirname(__file__), "..", "assets", "icon.ico"))
        
        # colunas e "vigas" sla o nome
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
            
        #tela/layout/ui 
        
        
        
            
          #tela  
        self.linhalateral = ctk.CTkFrame(self, width=150, corner_radius=0, fg_color="#181C1E")
        self.linhalateral.grid(row=0, column=0, sticky="nsw")
        
        self.linhalateral.grid_rowconfigure(98, weight=1)
        
        self.INFOdoSFT = ctk.CTkLabel(
            self.linhalateral,
            text=" v0.02private, new layout test",
            font=("Arial", 12) # versao f
            )
        self.INFOdoSFT.grid(row=99, column=0, padx=15, sticky="sw")
        
        
                   #aba superior
        self.logo_lay = ctk.CTkLabel(self.linhalateral, text="TIO PATINHAS", font=('Arial Black', 15, 'bold'))
        self.logo_lay.grid(row=0, pady=20, padx=10)
        
        self.linha_espaç1 = ctk.CTkLabel(self.linhalateral, text="----------")
        self.linha_espaç1.grid(row=1, column=0)
        
        self.linha_espaç2 = ctk.CTkLabel(self.linhalateral, text="----------")
        self.linha_espaç2.grid(row=9, column=0)
        
        self.but_inicio = ctk.CTkButton(self.linhalateral, text="Ínicio",  corner_radius=10, font=('Arial Black', 13))
        self.but_inicio.grid(row=2, pady=10, padx=10) # butao
        
        self.but_Gastos = ctk.CTkButton(self.linhalateral, text="Gastos", corner_radius=10, font=('Arial Black', 13))
        self.but_Gastos.grid(row=3, pady=10, padx=10) # butao
        
        self.but_Grafico = ctk.CTkButton(self.linhalateral, text="Gráfico",  corner_radius=10, font=('Arial Black', 13))
        self.but_Grafico.grid(row=4, pady=10, padx=10) # butao
        
        
        # tela, abas e resultados
        tela_aba = ctk.CTkFrame(self, width=600, corner_radius=10)
        tela_aba.grid(row=0, column=1, pady=20,  sticky='n')
        
        
        
        
if __name__ == "__main__":
    win = win()
    win.mainloop()