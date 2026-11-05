import API
import sys

from API import wallFront


def log(string):
    sys.stderr.write("{}\n".format(string))
    sys.stderr.flush()
class MouseInfo:

    def __init__(self):
        self.x=0
        self.y=0
        self.heading=0
        self.map=[[0 for k in range(16)] for l in range(16)]# 16 lists of 16 digits long
        self.wallMap=[[0 for k in range(16)] for l in range(16)]#0=?/1=wall up/2=wall right/4=wall back/8=wall left/add up to get combination of walls
        self.flood_map=[[None for k in range(16)] for l in range(16)]
        self.map[0][0]=1
        API.setColor(self.x,self.y,'c')
    def new_values(self,m):#computing update
        new_heading = (self.heading + m) % 8
        new_x = self.x
        new_y = self.y
        if new_heading==0:
            new_y=self.y+1
        elif new_heading==2:
            new_x=self.x+1
        elif new_heading==4:
            new_y=self.y-1
        elif new_heading==6:
            new_x=self.x-1
        return new_x, new_y, new_heading
    def update(self,m):#setting update
        """
        :param m: moves 0,1,2,3,4,5,6,7 (0=front, +1=+45 degrees) [m is relative, heading is absolute]
        :return:

        h=0:
            (m=0) y+1: h=0 [f]
            (m=2) x+1: h=2 [r,f]
            (m=4) y-1: h=4 [r,r,f]
            (m=6) x-1: h=6 [r,r,r,f]
        h=2:
            (m=0) x+1: h=2 [f]
            (m=2) y-1: h=4 [r,f]
            (m=4) x-1: h=6 [r,r,f]
            (m=6) y+1: h=0 [r,r,r,f]
        h=4:
            (m=0) y-1: h=4 [f]
            (m=2) x-1: h=6 [r,f]
            (m=4) y+1: h=0 [r,r,f]
            (m=6) x+1: h=2 [r,r,r,f]
        h=6:
            (m=0) x-1: h=6 [f]
            (m=2) y+1: h=0 [r,f]
            (m=4) x+1: h=2 [r,r,f]
            (m=6) y-1: h=4 [r,r,r,f]
        """
        self.x,self.y,self.heading=self.new_values(m)
    def update_walls(self):#TODO: adapt into get_moves()
        a=1
        b=2
        c=4
        d=8
        walls=0
        if self.heading == 0:
            if API.wallFront():
                walls += a
            if API.wallRight():
                walls += b
            if API.wallBack():
                walls += c
            if API.wallLeft():
                walls += d
        elif self.heading==2:
            if API.wallFront():
                walls+=b
            if API.wallRight():
                walls+=c
            if API.wallBack():
                walls+=d
            if API.wallLeft():
                walls+=a
        elif self.heading==4:
            if API.wallFront():
                walls+=c
            if API.wallRight():
                walls+=d
            if API.wallBack():
                walls+=a
            if API.wallLeft():
                walls+=b
        elif self.heading==6:
            if API.wallFront():
                walls+=d
            if API.wallRight():
                walls+=a
            if API.wallBack():
                walls+=b
            if API.wallLeft():
                walls+=c
        return walls

    def get_actions(self,m):
        moves=[]
        turns= m // 2
        if turns>0:
            moves=[API.turnRight]*turns
        moves.append(API.moveForward)
        return moves

    def execute(self, m):
        for a in self.get_actions(m):
            a()
        self.update(m)
        self.wallMap[self.x][self.y]=self.update_walls()
        self.map[self.x][self.y]=1
        API.setColor(self.x, self.y, 'c')
    def is_end(self):
        if self.x>6 and self.x<9 and self.y>6 and self.y<9 :
            return True
        else:
            return False
    def undo(self,m):
        API.turnLeft()
        API.turnLeft()
        API.moveForward()
        if m==0:
            API.turnRight()
            API.turnRight()
        elif m==2:
            API.turnRight()
        elif m==6:
            API.turnRight()
            API.turnRight()
            API.turnRight()
        # API.clearColor(self.x,self.y)
        # mi.map[self.x][self.y]=0
        if self.heading==0:
            self.y -= 1
        elif self.heading==2:
            self.x -= 1
        elif self.heading==4:
            self.y += 1
        elif self.heading==6:
            self.x += 1

        self.heading = (self.heading - m) % 8
        #go back to last place with another choice
    def heading_to_arrows(self):
        h="?"
        if self.heading==0:
            h="^"
        elif self.heading==2:
            h=">"
        elif self.heading==4:
            h="v"
        elif self.heading==6:
            h="<"
        return h
    def num_to_ascii(self,wall):
        """
        :inputs: int representing wall placements
        :return: visual representation of walls using text
        """
        cell=[" "," "," "]
        if wall & 5==5:
            cell[1]="="
        elif wall & 4:
            cell[1]="_"
        elif wall & 1:
            cell[1]="-"
        if wall & 2:
            cell[2]="|"
        if wall & 8:
            cell[0]="|"
        return "".join(cell)
    def write_map(self):
        """
        input: the text for each cell
        :return: a file with text representing walls visually
        """
        with open("map.txt", "w") as ascii_map:
            for y in range(15,-1,-1):
                for x in range(16):
                    ascii_map.write(self.num_to_ascii(self.wallMap[x][y]))
                    if x==0 and y==7:
                        log(self.wallMap[x][y])
                ascii_map.write("\n")
    def write_flood_map(self):
        with open("flood_map.txt", "w") as flood_map:
            for y in range(15, -1, -1):
                for x in range(16):
                    flood_map.write(f" {self.flood_map[x][y]} ")
                flood_map.write("\n")
            #TODO: write another file with the output of floodfill. if it is the same as the map.txt its correct
    def floodfill(self):
        """
        border=0
        label center cells=border
        labeled_cells=[x,y of labeled cells]
        while start isn't labeled:
            new_cells=[]
            border+=1
            for xy in labeled_cells:
                find all the coordinates with a 1-step move to unmarked squares
                append to list called new_cells with these coordinates
            for xy in new_cells:
                label border on coordinates
            labeled_cells=new_cells
        """
        border=0
        self.flood_map[7][7] = 0
        self.flood_map[7][8] = 0
        self.flood_map[8][7] = 0
        self.flood_map[8][8] = 0
        labeled_cells=[(7,7),(7,8),(8,7),(8,8)]
        while self.flood_map[0][0]==None:
            new_cells=[]
            border+=1
            for c in labeled_cells:
                for direction in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    neighbor=(c[0] + direction[0], c[1] + direction[1])
                    if 0<=neighbor[0]<16 and 0<=neighbor[1]<16 and self.flood_map[neighbor[0]][neighbor[1]]==None:
                        if direction==(0,1) and not self.wallMap[c[0]][c[1]]&1:
                            new_cells.append(neighbor)
                        if direction==(1,0) and not self.wallMap[c[0]][c[1]]&2:
                            new_cells.append(neighbor)
                        if direction==(0,-1) and not self.wallMap[c[0]][c[1]]&4:
                            new_cells.append(neighbor)
                        if direction==(-1,0) and not self.wallMap[c[0]][c[1]]&8:
                            new_cells.append(neighbor)
            for c in new_cells:
                self.flood_map[c[0]][c[1]]=border
            labeled_cells=new_cells
            #TODO:make mouse able to get fastest path using flood map

mi=MouseInfo()
def get_moves(mi: MouseInfo):
    moves=[]
    # if mi.heading==0:
    if not API.wallFront():
        m=0
        new_x, new_y, new_heading = mi.new_values(m)
        if mi.map[new_x][new_y] == 0:
            moves.append(m)
        log(f"new_x: {new_x}, new_y: {new_y}, move: {m}, map value at new x and new y: {mi.map[new_x][new_y]} ")
    if not API.wallRight():
        m=2
        new_x, new_y, new_heading = mi.new_values(m)
        if mi.map[new_x][new_y] == 0:
            moves.append(m)
        log(f"new_x: {new_x}, new_y: {new_y}, move: {m}, map value at new x and new y: {mi.map[new_x][new_y]} ")

    if not API.wallBack():
        m=4
        new_x, new_y, new_heading = mi.new_values(m)
        if mi.map[new_x][new_y] == 0:
            moves.append(m)
        log(f"new_x: {new_x}, new_y: {new_y}, move: {m}, map value at new x and new y: {mi.map[new_x][new_y]} ")

    if not API.wallLeft():
        m=6
        new_x, new_y, new_heading = mi.new_values(m)
        if mi.map[new_x][new_y] == 0:
            moves.append(m)
        log(f"new_x: {new_x}, new_y: {new_y}, move: {m}, map value at new x and new y: {mi.map[new_x][new_y]} ")

    return moves

def explore(mi: MouseInfo):
    # if mi.is_end():
    #     log("finished")
    #     log("-----")
    #     return "finished"
    # elif not mi.is_end():
    #     log("still going...")
    #     log("-----")
    moves=get_moves(mi)
    log(f"List of moves: {moves}")
    for m in moves:
        log(f"x: {mi.x}, y: {mi.y}, Heading: {mi.heading_to_arrows()}")
        mi.execute(m)
        log(f"executing: {m}")
        explore(mi)
        mi.undo(m)#go back to the position where you had another choice


def main(mi: MouseInfo):
    explore(mi)
    mi.write_map()
    mi.floodfill()
    mi.write_flood_map()
def main2():
    global heading, y, x
    last_turn=""
    log("Running...")
    API.setColor(0, 0, "G")
    API.setText(0, 0, "start")
    while True:
        while API.wallFront() and API.wallLeft():
            API.turnRight()
            last_turn = "R"
            API.setText(x, y, last_turn)
            heading = (heading + 2) % 8
        while API.wallFront() and API.wallRight():
            API.turnLeft()
            last_turn = "L"
            API.setText(x, y, last_turn)
            heading = (heading - 2) % 8
        while API.wallFront() and last_turn == "L":
            API.turnLeft()
            heading = (heading - 2) % 8
        while API.wallFront() and last_turn == "R":
            API.turnRight()
            heading = (heading + 2) % 8




        # while API.wallRight() and API.wallFront():
        #     API.turnLeft()
        #     heading = (heading - 1) % 4
        # while API.wallLeft() and API.wallFront():
        #     API.turnRight()
        #     heading = (heading + 1) % 4
        # while API.wallFront():
        #     if turn==API.turnLeft():
        #         API.turnLeft()
        #         heading = (heading - 1) % 4
        #         turn=API.turnRight()
        #     if turn==API.turnRight:
        #         API.turnRight()
        #         heading = (heading + 1) % 4
        #         turn = API.turnLeft()

        # random.choice([API.turnLeft(), API.turnRight()])

        log(x)
        log(y)
        log(f"heading {heading}")
        log("-----")

        API.moveForward()
        if heading==0: y+=1
        elif heading==2: x+=1
        elif heading==4: y-=1
        else: x-=1
        API.setColor(x,y,"c")

if __name__ == "__main__":
    main(mi)
