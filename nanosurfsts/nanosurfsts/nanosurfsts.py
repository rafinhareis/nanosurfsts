from os import walk,path,mkdir
from pandas import read_csv, DataFrame
from numpy import array, arange, log, sqrt,meshgrid, rot90
from scipy import interpolate
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt


def didv(x,y):
  h = x[1]-x[0]
  deri_y = []; deri_x =[]
  for i in range(1,len(x)-1):
    d = (y[i+1]-y[i-1])/(2*h)
    deri_x.append(x[i])
    deri_y.append(d)
  return [array(deri_x),array(deri_y)]

def i_V(x,y):
  I =[]; V= []
  for i in range(1,len(x)-1):
    V.append(x[i])
    I.append(y[i])
  return [array(V),array(I)]

def gap_type(df,p,delta):
    def didv(df, p):
      col = df.columns
      x = df[col[0]]; y_old = df[col[1]]*pow(10,9)
      n = int(p[0]*len(y_old)/100)
      if n%2 == 0:
          n+=1
      y = savgol_filter(y_old,n,p[1])

      h = (x[len(x)-1] - x[0])/len(x)
      deri_y = []; deri_x =[]
      for i in range(1,len(x)-1):
          d = (y[i+1]-y[i-1])/(2*h)
          deri_x.append(x[i])
          deri_y.append(d)
      return [array(deri_x),array(deri_y)/array(deri_y).max()]
    col = df.columns
    df = df.sort_values(by = [col[0]])
    x = df[col[0]]; y= df[col[1]]*pow(10,9)
    dx,dy = didv(df,p)
    f = interpolate.interp1d(dx, dy)
    marker1 = False; marker2 = False

    for i in range(len(dx)-1):
        if dx[0]<0:
            if dx[i]<=0 and dx[i+1]>=0:
               indice_x0 = i
               break
    marker1 = False; marker2 = False

    for i in range(len(dx)):
        if dx[0]<0:
          if i <= indice_x0:
            j= indice_x0-i
            if f(dx[j])<= delta and marker1 == False:
                xmin = dx[j]
            else:
               marker1 = True

          elif i > indice_x0:
            j= i 
            if f(dx[j])<= delta and marker2 == False:
                xmax = dx[j]
            else:
               marker2 = True
               
    try:
        gap = xmax-xmin
    except UnboundLocalError:
        xmin = 0
        xmax = 0
        gap = 0
    typ = abs(xmax) - abs(xmin)
    return [round(gap,2),round(typ,2),xmin,xmax]


class File:
    def __init__(self):
        self.path_file = './'
    
    def load_file(self):
        df = read_csv ( self.path_file, sep= ';', names= ['x','y','z'])
        first_value = df[df.columns[0]].iloc[0] 
        V = []
        for i in range(1,len(df)):
            if df[df.columns[0]].iloc[i]  == first_value:
                count = i
                #V.append(df[df.columns[0]].iloc[i])
                break
            else:
                V.append(df[df.columns[0]].iloc[i])

        n = int(len(df)/count)

        dataframes = []
        names = []
        for j in range(n):
            sts=[]
            volta =[]

            for i in range(len(df)):
                if i<count :
                    filtro_alto = 18*pow(10,-9)
                    filtro_baixo = -filtro_alto
                    voltagem = df[df.columns[0]].iloc[i]
                    corrente = df[df.columns[2]].iloc[i+j*count]
                    if corrente>filtro_baixo and corrente < filtro_alto:
                        volta.append(voltagem)
                        sts.append(corrente)
                    else:
                        pass
                else:
                    break

            V_new = volta
            df_new = DataFrame(V_new,columns = ['V'])
            df_new['I'+str(j)] = sts
            names.append(str(j) )
            dataframes.append(df_new)

        self.data = dataframes
        self.names = names

    def heatmap(self):
        n = len(self.data)
        m = int(sqrt(n))
        matriz = []
        for i in range(m):
            col = []
            for j in range(m):
                col.append(self.data[i*m+j])
            matriz.append(array(col))
        matriz = array(matriz)
        return matriz


    def select_sts(self, n = []):
        folder_save = 'sts_saves'
        file = self.path_file[:-4]
        for i in range(1,len(file)):
            if file[len(file) -i] == '/':
                ct = len(file) -i
                break
        folder_name = path.join(folder_save,file[ct:])
        try: 
            mkdir(folder_save )
        except FileExistsError:
            pass
        
        paste = folder_save+folder_name
        try:
            mkdir(paste)
        except FileExistsError:
            pass
        
        for i in range(len(self.data)):
            if (i in n) == False:
                name = path.join(paste,self.names[i])
                self.data[i].to_csv(name +'.txt')


    def load_saves_files(self):
        names = []
        dataframes = []
        for diretorio, subpastas, arquivos in walk(self.path_file):
            for arq in arquivos:
                name = path.join( self.path_file,arq)
                df =  read_csv(name )
                df = df.drop( df.columns[0],axis = 1)
                dataframes.append(df )
                names.append(arq)
        self.data = dataframes
        self.names = names

    def plot(self, figsize = ( 10,600),p = [10,1],delta = 0.1):
        m1 = 0
        m2 = len(self.data)
        self.list_gap = []
        self.list_shift = []
        fig, figura = plt.subplots((m2-m1),2,figsize= figsize)
        for i in range(m1,m2):
            data = self.data[i]
            columns = data.columns
            V = data[columns[0]]

            I_old = data[columns[1]]*pow(10,9)

            n = int(p[0]*len(I_old)/100)
            if n%2 == 0:
                n+=1
            try:


                
                I = savgol_filter(I_old,n,p[1])
                figura[i][0].plot(V,I,label = self.names[i] )
                figura[i][0].legend()
                gap,typ,xmin,xmax = gap_type(data,p,delta)
                self.list_gap.append(gap)
                self.list_shift.append(typ)
                dx,dy = didv(V,I)
                dyinterp = interpolate.interp1d(dx,dy)
                ymin = dyinterp(xmin)
                ymax = dyinterp(xmax)
                figura[i][1].scatter([xmin,xmax],[ymin,ymax],s = 20, color = 'red')
                figura[i][1].plot(dx,dy, label = 'Gap '+ str(gap)+ 'Type ' + str(typ))
                figura[i][1].legend()
            except ValueError:
                pass

    def plot_hist(self, figsize = (20,10), p =(10,1),delta = 0.1):
        m1 = 0
        m2 = len(self.data)
        self.list_gap = []
        self.list_shift = []
        fig, figura = plt.subplots(1,2,figsize= figsize)
        for i in range(m1,m2):
            data = self.data[i]
            columns = data.columns
            V = data[columns[0]]

            I_old = data[columns[1]]*pow(10,9)

            n = int(p[0]*len(I_old)/100)
            if n%2 == 0:
                n+=1
            try:
                I = savgol_filter(I_old,n,p[1])
                gap,typ,xmin,xmax = gap_type(data,p,delta)
                self.list_gap.append(gap)
                self.list_shift.append(typ)
            except ValueError:
                pass
        
        figura[0].hist(self.list_gap,10,rwidth = 0.8)
        figura[0].set_xticks(arange(0,max(self.list_gap)+0.5,0.5),arange(0,max(self.list_gap)+0.5,0.5) )
        figura[1].hist(self.list_shift,10,rwidth = 0.8)

    def plot_all(self, figsize = ( 30,600),p = [10,1]):
        m1 = 0
        m2 = len(self.data)
        fig, figura = plt.subplots((m2-m1),5,figsize= figsize)
        for i in range(m1,m2):
            data = self.data[i]
            columns = data.columns
            V = data[columns[0]]

            I_old = data[columns[1]]*pow(10,9)

            n = int(p[0]*len(I_old)/100)
            if n%2 == 0:
                n+=1
            
            I = savgol_filter(I_old,n,p[1])

            figura[i][0].plot(V,I,label = self.names[i] )
            figura[i][0].legend()

            dx,dy = didv(V,I)

            figura[i][1].plot(dx,dy)

            figura[i][2].plot(V,log(abs(I)) )

            figura[i][3].plot(log(V),log(abs(I)) )

            dxlog,dylog = didv(V,log(abs(I)))

            figura[i][4].plot(dxlog,dylog )




