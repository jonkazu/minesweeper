# Minesweeper GUI                 
import sys 
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import random
# import threading

# sys.setrecursionlimit(67108864) 
# threading.stack_size(1024*1024) 

MS_SIZE = 25   # ゲーム盤のサイズ
CLOSE, OPEN, FLAG = 0, 1, 2

# ★今までに作成したコードからGameクラスをコピー★

class Game:
    def __init__(self, number_of_mines = 200):
        """ ゲーム盤の初期化
        
        Arguments:
        number_of_mines -- 地雷の数のデフォルト値は10

        Side effects:
        mine_map[][] -- 地雷マップ(-1: 地雷，>=0 8近傍の地雷数)
        game_board[][] -- 盤面 (0: CLOSE(初期状態), 1: 開いた状態, 2: フラグ)

        """
        self.init_game_board()
        self.init_mine_map(number_of_mines)
        self.count_mines()

    def init_game_board(self):
        """ ゲーム盤を初期化 """
        self.game_board = [[0 for i in range(MS_SIZE)] for j in range(MS_SIZE)]
        
    def init_mine_map(self, number_of_mines):
        """ 地雷マップ(self->mine_map)の初期化
        Arguments:
        number_of_mines -- 地雷の数
        
        地雷セルに-1を設定する.    
        """
        self.mine_map = [[0 for i in range(MS_SIZE)] for j in range(MS_SIZE)]
        if number_of_mines > MS_SIZE*MS_SIZE: #爆弾の数が大きいとき
            number_of_mines = MS_SIZE*MS_SIZE
               
        while number_of_mines>0:              
            x=random.randint(0,MS_SIZE-1)
            y=random.randint(0,MS_SIZE-1)
            if self.mine_map[y][x] == 0:
                self.mine_map[y][x] = -1
                number_of_mines -= 1 
            

    def count_mines(self):
        """ 8近傍の地雷数をカウントしmine_mapに格納 
        地雷数をmine_map[][]に設定する．
        """
        for y in range(MS_SIZE):
            for x in range(MS_SIZE):
                if self.mine_map[y][x] < 0:
                    for t in range(-1,2):
                        for s in range(-1,2):
                            if (x+s) >= 0 and (x+s) < MS_SIZE and (y+t)>=0 and (y+t) < MS_SIZE and self.mine_map[y+t][x+s] > -1:
                                self.mine_map[y+t][x+s]+=1
        
        #print(self.mine_map)
    
    def open_cell(self, x, y):
        """ セル(x, y)を開ける
        Arguments:
        x, y -- セルの位置
        
        Returns:
          True  -- 8近傍セルをOPENに設定．
                   ただし，既に開いているセルの近傍セルは開けない．
                   地雷セル，FLAGが設定されたセルは開けない．
          False -- 地雷があるセルを開けてしまった場合（ゲームオーバ）
        """
        # <-- (STEP 4) ここにコードを追加
        if self.mine_map[y][x] == -1:
            return False
        elif self.game_board[y][x]==0:
            for t in range(-1,2):
                for s in range(-1,2):
                    if (x+s) >= 0 and (x+s) < MS_SIZE and (y+t)>=0 and (y+t) < MS_SIZE and self.mine_map[y+t][x+s] > -1 and self.game_board[y+t][x+s]==0:
                        self.game_board[y+t][x+s]=1

        return True
    
    def flag_cell(self, x, y):
        """
        セル(x, y)にフラグを設定する，既に設定されている場合はCLOSE状態にする
        """
        if self.game_board[y][x] == 0:
            self.game_board[y][x] = 2

        elif self.game_board[y][x] == 2:
            self.game_board[y][x] = 0

            
    def is_finished(self):
        """ 地雷セル以外のすべてのセルが開かれたかチェック """
        c1=0
        c2=0
        for y in range(MS_SIZE):
            for x in range(MS_SIZE):
                if self.game_board[y][x]==1:
                    c1+=1
                if self.mine_map[y][x] > -1:
                    c2+=1

        if c1==c2:
            return True

        return False
    


class MyPushButton(QPushButton):
    
    def __init__(self, text, x, y, parent):
        """ セルに対応するボタンを生成 
        Arguments:
            self
            text -- ボタンに表示する文字列
            x, y -- ボタンの位置
            parent -- MindsweeperWindowクラスのインスタンス
        """
        super(MyPushButton, self).__init__(text, parent)
        self.parent = parent
        self.x = x
        self.y = y
        self.setMinimumSize(40, 20)
        self.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)

    def set_bg_color(self, colorname):
        """ セルの色を指定する
        Arguments:
            self
            colorname: 文字列 -- 色名 (例, "white")
        """
        self.setStyleSheet("MyPushButton{{background-color: {}}}".format(colorname))
        
    def on_click(self):
        """ セルをクリックしたときの動作 """
        modifiers = QApplication.keyboardModifiers()
        #フラグ処理
        if modifiers == Qt.ShiftModifier:
            self.parent.game.flag_cell(self.y, self.x)
            self.parent.show_cell_status()
        else:
            if self.parent.game.game_board[self.x][self.y] != 2:
                if self.parent.game.open_cell(self.y, self.x):
                    self.parent.show_cell_status()
                    #ゲーム終了かどうか
                    if self.parent.game.is_finished():
                        self.parent.show_cell_status3()
                        QMessageBox.information(self, "Game clear", "ゲームクリア!")   
                        self.parent.close()


                #ゲームオーバー
                else:
                    self.parent.show_cell_status2(self.x,self.y)
                    QMessageBox.information(self, "Game over", "ゲームオーバー!")
                    self.parent.close()

    
class MinesweeperWindow(QMainWindow):
    
    def __init__(self):
        """ インスタンスが生成されたときに呼び出されるメソッド """
        super(MinesweeperWindow, self).__init__()
        self.game = Game()
        self.initUI()
        #self.show_cell_status()

    def initUI(self):
        """ UIの初期化 """        
        self.resize(200, 200) 
        self.setWindowTitle('Minesweeper')
        
        # ★以下，コードを追加★
        self.marks = ['x', ' ', 'P']
        self.hbox=[0 for i in range(MS_SIZE)]
        self.button = [[0 for i in range(MS_SIZE)] for j in range(MS_SIZE)]
        
        self.vbox = QVBoxLayout(spacing=0)
        for j in range(MS_SIZE):
            self.hbox[j] = QHBoxLayout()
            self.hbox[j].addStretch(1)
            for i in range(MS_SIZE):
                self.button[j][i]=MyPushButton(self.marks[self.game.game_board[j][i]],j,i,self)
                self.button[j][i].clicked.connect(self.button[j][i].on_click)
                self.hbox[j].addWidget(self.button[j][i])
            self.hbox[j].addStretch(1)
            self.vbox.addLayout(self.hbox[j])

        self.statusBar().showMessage('Shift+クリックでフラグをセット')
        self.show_cell_status()


    def show_cell_status(self):
        """ ゲームボードを表示 """
        for j in range(MS_SIZE):
            for i in range(MS_SIZE):
                if self.game.game_board[j][i] == 1:
                    self.button[j][i].setText(str(self.game.mine_map[j][i]))
                    self.button[j][i].set_bg_color('green')
                elif self.game.game_board[j][i] == 2:
                    self.button[j][i].setText(self.marks[self.game.game_board[j][i]])
                    self.button[j][i].set_bg_color("yellow")
                else:
                    self.button[j][i].setText(self.marks[self.game.game_board[j][i]])
                    self.button[j][i].set_bg_color('gray')
        
        container = QWidget()
        container.setLayout(self.vbox)
        # QVBoxLayout(spacing = 0)
        # QHBoxLayout(spacing = 0)
        self.setCentralWidget(container)
        
        self.show()

    def show_cell_status2(self,x,y):
        """ ゲームボードを表示 """

        #ゲームオーバーの時に表示 
        #地雷はピンク、それ以外はグレーで表示
        
        for j in range(MS_SIZE):
            for i in range(MS_SIZE):
                self.button[j][i].setText(str(self.game.mine_map[j][i]))
                #踏んでしまった地雷の場所は赤色
                if j==x and i==y:
                    self.button[j][i].set_bg_color('red')
                #地雷がないのに旗を立ててしまっていた場合はオレンジ色
                elif self.game.mine_map[j][i] != -1 and self.game.game_board[j][i] == 2:
                    self.button[j][i].set_bg_color('orange')
                elif self.game.mine_map[j][i] == -1:
                    self.button[j][i].set_bg_color('pink')
                else:
                    self.button[j][i].set_bg_color('gray')


        container = QWidget()
        container.setLayout(self.vbox)
        # QVBoxLayout(spacing = 0)
        # QHBoxLayout(spacing = 0)
        self.setCentralWidget(container)
    

    def show_cell_status3(self):
        """ ゲームボードを表示 """
        #ゲームクリアの時に表示 
        #地雷はピンク、それ以外はグレーで表示
        
        for j in range(MS_SIZE):
            for i in range(MS_SIZE):
                self.button[j][i].setText("○")
                self.button[j][i].set_bg_color('red')
        
        
        container = QWidget()
        container.setLayout(self.vbox)
        # QVBoxLayout(spacing = 0)
        # QHBoxLayout(spacing = 0)
        self.setCentralWidget(container)

def main():
    app = QApplication(sys.argv)
    w = MinesweeperWindow()
    app.exec_()
            
if __name__ == '__main__':
    main()