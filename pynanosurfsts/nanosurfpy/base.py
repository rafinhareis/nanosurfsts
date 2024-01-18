from os import walk,path,mkdir,listdir
from pandas import read_csv, DataFrame
from numpy import array, arange, log, sqrt,meshgrid, rot90
from scipy import interpolate
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import ipywidgets as widgets

print('Software de visualizacao de arquivos de STS Nanosurf v1.2.0. Arquivos tipo csv (x,y,z) ')
print('By Rafael Reis, contato rafinhareis17@gmail.com')
print('Se sentir no fundo do coracaozinho, poe meu nome no artigo =D')

def didv(x,y):
    h = x[1]-x[0]
    deri_y = []; deri_x =[]
    for i in range(1,len(x)-1):
        d = (y[i+1]-y[i-1])/(2*h)
        deri_x.append(x[i])
        deri_y.append(d)
    deri_y=array(deri_y)
    return [array(deri_x),deri_y/deri_y.max()]

def i_V(x,y):
  I =[]; V= []
  for i in range(1,len(x)-1):
    V.append(x[i])
    I.append(y[i])
  return [array(V),array(I)]

def gap_type(dx,dy,delta):
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

def load_file(path):
    df = read_csv ( path, sep= ';', names= ['x','y','z'])
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

    return [dataframes,names]

def to_table(path_files):
    files = listdir(path_files)
    arq_I = open(path_files+'Dataframe_I_complete.csv','w')
    arq_didv = open(path_files+'Dataframe_dIdv_complete.csv','w')
    lines_I = []
    lines_didv = []
    marker=False
    marker2 = True
    for item in files:
        if '.txt' in item:
            df = read_csv(path_files+item)
            number = ''
            for car in item:
                if car=='_':
                    break
                number+=car
            col = df.columns
            x=df[col[0]];y=df[col[1]];dy=df[col[2]]
            dy=dy/dy.max()
            if marker == False:
                tam = len(x)
                xlimmin = x.min()
                xlimmax = x.max()
                lines_I.append([col[0]+'_'+number,',',col[1]+'_'+number])
                lines_didv.append([col[0]+'_'+number,',',col[2]+'_'+number])
                marker = True
                for j in range(len(x)):
                    lines_I.append([x[j],',',y[j]])
                    lines_didv.append([x[j],',',dy[j]])
            else:
                if x.min()>=xlimmin:
                    xlimmin=x.min()
                if x.max()<=xlimmax:
                    xlimmax=x.max()
                lines_I[0] = lines_I[0]+ [',',col[0]+'_'+number,',',col[1]+'_'+number]
                lines_didv[0] = lines_didv[0]+ [',',col[0]+'_'+number,',',col[2]+'_'+number]

                if len(x)<=tam:
                    for k in range(len(x)):
                        lines_I[k+1] = lines_I[k+1]+ [',',x[k],',',y[k]]
                        lines_didv[k+1] = lines_didv[k+1]+ [',',x[k],',',dy[k]]
                else:
                    for k in range(len(x)):
                        if k <tam:
                            lines_I[k+1] = lines_I[k+1]+ [',',x[k],',',y[k]]
                            lines_didv[k+1] = lines_didv[k+1]+ [',',x[k],',',dy[k]]
                        else:
                            lines_I.append([x[j],',',y[j]])
                            lines_didv.append([x[j],',',y[j]])
                    tam=len(x)
    for line in lines_I:
        line = list(map(lambda x:str(x),line))
        l = ''
        for c in line:
            l+=c 
        arq_I.writelines(l+'\n')
    arq_I.close()
    for line in lines_didv:
        line = list(map(lambda x:str(x),line))
        l = ''
        for c in line:
            l+=c 
        arq_didv.writelines(l+'\n')
    arq_didv.close()

    for item in files:
        if '.txt' in item:
            df = read_csv(path_files+item)
            number = ''
            for car in item:
                if car=='_':
                    break
                number+=car

            col = df.columns
            x=df[col[0]];y=df[col[1]];dy=df[col[2]]
            dy=dy/dy.max()
            if marker2:
                xnew  = arange(xlimmin,xlimmax,0.01)
                f = interpolate.interp1d(x,y)
                g = interpolate.interp1d(x,dy)
                df2 = DataFrame({'V':xnew,'I_'+number:f(xnew)})
                df3 = DataFrame({'V':xnew,'didv_'+number:g(xnew)})
                marker2=False
            else:
                f = interpolate.interp1d(x,y)
                g = interpolate.interp1d(x,dy)
                df2['I_'+number]=f(xnew)
                df3['didv_'+number]=g(xnew)
    df2 = df2.set_index('V')
    df3 = df3.set_index('V')
    df2.to_csv(path_files+'Dataframe_I_limeted_by_V.csv')
    df3.to_csv(path_files+'Dataframe_didv_limeted_by_V.csv')



class select_sts:
    def __init__(self,path_file,n,smooth = 5,delta = 10):
        self.path_file = path_file
        self.file = load_file(path_file)    

        def select_sts(path_file, n = [],smooth = 5,delta = 10):
            file = load_file(path_file)
            folder_save = 'sts_saves'
            for i in range(1,len(path_file[:-4])):
                if path_file[len(path_file[:-4]) -i] == '/':
                    ct = len(path_file[:-4]) -i
                    break
            try:
                #folder_name = path.join(folder_save,path_file[:-4][ct:])
                folder_name= folder_save+path_file[:-4][ct:]
            except UnboundLocalError:
                ct = 0
                #folder_name = path.join(folder_save,path_file[ct:-4])
                folder_name= folder_save+'/'+ path_file[:-4][ct:]
            try: 
                mkdir(folder_save )
            except FileExistsError:
                pass
                
            paste =folder_name
            try:
                mkdir(paste)
            except FileExistsError:
                pass
            
            for i in range(len(file[0])):
                if (i in n) == False:
                        name = path.join(paste,file[1][i])
                        x= file[0][i][file[0][i].columns[0]];y = file[0][i][file[0][i].columns[1]]*pow(10,9)
                        p = int(smooth*len(y)/100)
                        if p%2==0:
                            p+=1
                            y = savgol_filter(y,p,1)
                        elif p==0:
                            pass
                        else:
                            y = savgol_filter(y,p,1)
                        dx,dy = didv(x,y)
                        gap,typ,xmin,xmax = gap_type(dx,dy,delta/100)
                        if abs(typ)<=0.1:
                            tipo = 'neutro'
                        elif typ<-0.1:
                            tipo = 'n'
                        else:
                            tipo = 'p'
                        f = interpolate.interp1d( file[0][i][file[0][i].columns[0]],file[0][i][file[0][i].columns[1]])
                        g = interpolate.interp1d(dx,dy)
                        xnew = arange(dx.min(),dx.max()-0.01,0.01)
                        df_new = DataFrame({'V':xnew,'I(nA)':f(xnew),'didv':g(xnew),'gap': str(gap),'tipo':str(tipo)}   )
                        df_new = df_new.set_index('V')
                        if ct ==0:
                            df_new .to_csv(name +'_'+path_file[:-4][ct:]+'.txt') 
                        else:
                            df_new .to_csv(name +'_'+path_file[:-4][ct+1:]+'.txt') 
            print("arquivos salvos na pasta "+ paste)
            to_table(paste+'/')
        select_sts(path_file,n,smooth,delta)
        
class Display:
    def __init__(self,path_file):
        self.path_file = path_file
        self.file = load_file(path_file)
        def plot_curve(curve = 0,smooth = 5,delta = 10):
                file = self.file
                curve = int(curve)
                fig,ax= plt.subplots(1,2,figsize=(20,8))
                dfs = file[0]
                columns = dfs[curve].columns
                x = dfs[curve][columns[0]];y = dfs[curve][columns[1]]*pow(10,9)
                p = int(smooth*len(y)/100)
                if p%2==0:
                    p+=1
                    y = savgol_filter(y,p,1)
                elif p==0:
                    pass
                else:
                    y = savgol_filter(y,p,1)

                ax[0].plot(x,y)
                ax[0].set_xlabel('Sample bias (V)')
                ax[0].set_ylabel('Current (nA)')

                dx,dy = didv(x,y)
                gap,typ,xmin,xmax = gap_type(dx,dy,delta/100)
                if abs(typ)<=0.1:
                    tipo = 'neutro'
                elif typ<-0.1:
                    tipo = 'n'
                else:
                    tipo = 'p'
                dyinterp = interpolate.interp1d(dx,dy)
                ymin = dyinterp(xmin)
                ymax = dyinterp(xmax)
                ax[1].scatter([xmin,xmax],[ymin,ymax],s = 50, color = 'red')
                ax[1].plot(dx,dy, label = 'Gap '+ str(gap)+ ': Type ' + tipo)
                ax[1].set_xlabel('Sample bias (V)')
                ax[1].set_ylabel('dI/dV (arb. units)')
                ax[1].legend()    

        widgets.interact(plot_curve,curve= (0.,len(self.file[0]),1), smooth = (0.,20,.5),delta = (0.,100,1))

