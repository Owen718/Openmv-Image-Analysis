from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets,QtGui
from PyQt5.QtCore import *
import serial
import serial.tools.list_ports
from cv2 import cv2
import sys
import numpy as np
import win32gui
from matplotlib import pyplot as plt
import psutil
import win32api
import re
Lab_list = [0,0,0,0,0,0]
position_list = [0,0,0,0]  #[x,y,wide,height]
global img_cv, point1, point2,g_rect,cut_img

def get_window_jpg():  #获得Frame Buffer的图像
    global img_cv
    hwnd = win32gui.FindWindow('pygame', 'Frame Buffer')
    screen = QtWidgets.QApplication.primaryScreen()
    img = screen.grabWindow(hwnd).toImage()
    #print(hwnd)
    img.save("screenshot.jpg")
    img_cv = cv2.imread("screenshot.jpg")


    

def lab_data():  #lab数据处理及范围输出
    global Lab_list,cut_img
#    img=cv2.imread("screenshot.jpg",cv2.IMREAD_COLOR)
    img_lab = cv2.cvtColor(cut_img, cv2.COLOR_BGR2LAB)
    ############lab数据与直方图################
    l,a,b = cv2.split(img_lab)
    Lab_list = [np.max(l)*100/255,np.min(l)*100/255,np.max(a)-128,np.min(a)-128,np.max(b)-128,np.min(b)-128]  #求lab值的范围
    #print("L_max:",np.max(l)*100/255,"L_min:",np.min(l)*255/100)  #opencv已将值缩放，我们需要缩放回去。
    #print("A_max:",np.max(a)-128,"A_min:",np.min(a)-128)
    #print("B_max:",np.max(b)-128,"B_min:",np.min(b)-128)
    #label 的内容
    win.LabLAB1.setText("L:"+str(Lab_list[1])+"-"+str(Lab_list[0])+"  X:"+str(position_list[0]))
    win.LabLAB2.setText("A:"+str(Lab_list[3])+"-"+str(Lab_list[2])+"  Y:"+str(position_list[1]))
    win.LabLAB3.setText("B:"+str(Lab_list[5])+"-"+str(Lab_list[4])+"  Width:"+str(position_list[2])+"  Height:"+str(position_list[3]))
    win.L_set_edit.setText(str(Lab_list[1])+"-"+str(Lab_list[0]))
    win.A_set_edit.setText(str(Lab_list[3])+"-"+str(Lab_list[2]))
    win.B_set_edit.setText(str(Lab_list[5])+"-"+str(Lab_list[4]))
    win.X_set_edit.setText(str(position_list[0]))
    win.Y_set_edit.setText(str(position_list[1]))
    win.height_set_edit.setText(str(position_list[3]))
    win.width_set_edit.setText(str(position_list[2]))

    
    win.Y_set_edit.setText(str(position_list[1]))

def RGB_hist_show():  #RGB直方图输出
    '''
    RGB三通道颜色直方图
    :param:NONE
    :return：NONE
    # 按R、G、B三个通道分别计算颜色直方图
    '''
    global img_cv
    img=img_cv
    b_hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    g_hist = cv2.calcHist([img], [1], None, [256], [0, 256])
    r_hist = cv2.calcHist([img], [2], None, [256], [0, 256])
        
    # 显示3个通道的颜色直方图
    plt.plot(b_hist, label='B', color='blue')
    plt.plot(g_hist, label='G', color='green')
    plt.plot(r_hist, label='R', color='red')
    plt.legend(loc='best')
    plt.xlim([0, 256])
   # print(max(b_hist),min(b_hist),max(g_hist),min(g_hist),max(r_hist),min(r_hist))
    plt.show()

def on_mouse(event, x, y, flags, param):
    '''
    鼠标画框，左键点击打点，左键拖拽画框
    :param :event,x,y,flags,param
    :return: NONE
    '''
    global img_cv, point1, point2,g_rect,cut_img,position_list
    img2 = img_cv.copy()
    if event == cv2.EVENT_LBUTTONDOWN:  # 左键点击,则在原图打点
     #   print("1-EVENT_LBUTTONDOWN")
        point1 = (x, y)
        cv2.circle(img2, point1, 10, (0, 255, 0), 5)
        cv2.resizeWindow('image',640,480)
        cv2.imshow('image', img2)
 
    elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):  # 按住左键拖曳，画框
     #   print("2-EVENT_FLAG_LBUTTON")
        cv2.rectangle(img2, point1, (x, y), (255, 0, 0), thickness=2)
        cv2.resizeWindow('image',640,480)
        cv2.imshow('image', img2)
 
    elif event == cv2.EVENT_LBUTTONUP:  # 左键释放，显示
     #   print("3-EVENT_LBUTTONUP")
        point2 = (x, y)
        cv2.rectangle(img2, point1, point2, (0, 0, 255), thickness=2)
        cv2.resizeWindow('image',640,480)
        cv2.imshow('image', img2)
        if point1!=point2:
            min_x = min(point1[0], point2[0])
            min_y = min(point1[1], point2[1])
            width = abs(point1[0] - point2[0])
            height = abs(point1[1] - point2[1])
            g_rect=[min_x,min_y,width,height]
            position_list[0]=min_x
            position_list[1]=min_y
            position_list[2]=width
            position_list[3]=height
            cut_img = img_cv[min_y:min_y + height, min_x:min_x + width]
 #           cv2.imshow('ROI', cut_img)
            lab_data()
          #  print(Lab_list)   

def get_image_roi(rgb_image):
    '''
    获得用户ROI区域的rect=[x,y,w,h]
    :param rgb_image:
    :return:
    '''
#    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    global g_rect
    img=rgb_image
    cv2.namedWindow('image')
    cv2.resizeWindow('image',640,480)
    while True:
        cv2.setMouseCallback('image', on_mouse)
        cv2.resizeWindow('image',640,480)
        cv2.startWindowThread()  # 加在这个位置
        cv2.imshow('image', img)
        key=cv2.waitKey(0)
        if cv2.getWindowProperty('image', cv2.WND_PROP_AUTOSIZE) < 1:
            break
     
    cv2.destroyAllWindows()
#    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return g_rect



#主界面UI
class WindowClass(QWidget):  #创建一个windowclass类
    def __init__(self,parent=None):   #初始化
        super(WindowClass, self).__init__(parent)
        win_layout =QHBoxLayout() #整体布局
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.data_receive)
      
      

        self.resize(250,300)  #窗口大小
        self.setWindowTitle("Openmv image analyse")  #窗口标题
         #label 对象
        self.LabLAB1 = QtWidgets.QLabel()
        self.LabLAB2 = QtWidgets.QLabel()
        self.LabLAB3 = QtWidgets.QLabel()
        #lab 范围 label 的内容
        self.LabLAB1.setText("L:"+str(Lab_list[1])+"-"+str(Lab_list[0])+"  X:"+str(position_list[0]))
        self.LabLAB2.setText("A:"+str(Lab_list[3])+"-"+str(Lab_list[2])+"  Y:"+str(position_list[1]))
        self.LabLAB3.setText("B:"+str(Lab_list[5])+"-"+str(Lab_list[4])+"  Width:"+str(position_list[2])+"  Height:"+str(position_list[3]))
        #字体设置
        font = QtGui.QFont()
        font.setPointSize(12)
        
        self.LabLAB1.setFont(font)
        self.LabLAB2.setFont(font)
        self.LabLAB3.setFont(font)
        #lab_set label lab值标签的内容
        self.labLAB_set1 = QtWidgets.QLabel()
        self.labLAB_set2 = QtWidgets.QLabel()
        self.labLAB_set3 = QtWidgets.QLabel()
        
        self.labLAB_set1.setText("L:")
        self.labLAB_set2.setText("A:")
        self.labLAB_set3.setText("B:")


        font.setPointSize(12)
        self.labLAB_set1.setFont(font)
        self.labLAB_set2.setFont(font)
        self.labLAB_set3.setFont(font)
        

        

        #lab值设定编辑框
        self.L_set_edit = QtWidgets.QLineEdit()
        self.A_set_edit = QtWidgets.QLineEdit()
        self.B_set_edit = QtWidgets.QLineEdit()
        

        self.L_set_edit.setText(str(Lab_list[1])+"-"+str(Lab_list[0]))
        self.A_set_edit.setText(str(Lab_list[3])+"-"+str(Lab_list[2]))
        self.B_set_edit.setText(str(Lab_list[5])+"-"+str(Lab_list[4]))
    #    self.L_set_edit.setMaximumWidth(QtGui.QFontMetrics(QtGui.QFont(self.L_set_edit.text())).width(self.L_set_edit.text()))
     

        self.L_set_edit.adjustSize()
        self.A_set_edit.adjustSize()
        self.B_set_edit.adjustSize()

        #xy_set lable
        self.x_set_lab = QtWidgets.QLabel()
        self.y_set_lab = QtWidgets.QLabel()
        #width height lable
        self.width_set_lab = QtWidgets.QLabel()
        self.height_set_lab = QtWidgets.QLabel()
        #xy_set label的内容
        self.x_set_lab.setText("X:")
        self.y_set_lab.setText("Y:")
        self.x_set_lab.setFont(font)
        self.y_set_lab.setFont(font)
        #height,width label的内容
        self.height_set_lab.setText("Height:")
        self.width_set_lab.setText("Width:")

        self.X_set_edit = QtWidgets.QLineEdit()
        self.Y_set_edit = QtWidgets.QLineEdit()

        self.X_set_edit.setText(str(position_list[0]))
        self.Y_set_edit.setText(str(position_list[1]))
        #width,height edit

        self.width_set_edit = QtWidgets.QLineEdit()
        self.height_set_edit = QtWidgets.QLineEdit()

        self.width_set_edit.setText(str(position_list[2]))
        self.height_set_edit.setText(str(position_list[3]))
        ##################################################
        #盘符下拉框 ，盘符标签

        self.device_lab = QtWidgets.QLabel()
        self.device_lab.setText("请选择openmv的盘符:")
        self.device_lab.setFont(font)
        self.device_lab.setScaledContents(True)
        self.device_combobox = QtWidgets.QComboBox()


        ##################################################


        #com端口下拉框 , com标签，串口信息标签,检测按钮
        self.s1_lable_com = QtWidgets.QLabel()
        self.s1_box_1 =QtWidgets.QComboBox()
        self.s1_lable_com.setText("COM:")
        self.s1_lable_com.setScaledContents(True)
      #  self.s1_lable_com.setFixedWidth(28)   #设定label宽度
        self.com_state_lable = QtWidgets.QLabel()
        self.com_state_lable.setText("当前串口为：无")
        self.com_state_lable.setFont(font)
        
      
        self.s1_lable_com.setFixedWidth(QtGui.QFontMetrics(QtGui.QFont(self.s1_lable_com.text())).width(self.s1_lable_com.text()))   #设定label宽度
  
        

        
        self.s1_lable_com.setFont(font)
        self.s1_comcheck_btn1 = QtWidgets.QPushButton("检测串口") 
        self.s1_comopen_btn2 = QtWidgets.QPushButton("打开串口")
        self.s1_comclose_btn3 = QtWidgets.QPushButton("关闭串口")
        self.s1_savedata_btn4 = QtWidgets.QPushButton("保存ROI和LAB阈值到openmv")
        self.s1_comclear_btn5 = QtWidgets.QPushButton("清空ROI和LAB数据")
        self.s1_comclose_btn3.setEnabled(False)
        self.s1_comdata_label = QtWidgets.QLabel("串口接收到的数据：")
        self.s1_comdata_receive =QtWidgets.QLineEdit()
     
        



        self.btn_1=QPushButton("连接openmv")
        self.btn_2=QPushButton("截取图像")
        self.btn_3=QPushButton("显示RGB直方图")
        '''
        按钮美化
        self.btn_3.setStyleSheet("QPushButton{color:black}"
                                  "QPushButton:hover{color:red}"
                                  "QPushButton{background-color:rgb(78,255,255)}"
                                  "QPushButton{border:2px}"
                                  "QPushButton{border-radius:10px}"
                                  "QPushButton{padding:2px 4px}")
        '''
        #########左控件布局#########
        lwg = QWidget() #左边的控件
        vlayout=QVBoxLayout()  
        vlayout.addWidget(self.LabLAB1)
        vlayout.addWidget(self.LabLAB2)
        vlayout.addWidget(self.LabLAB3)
        vlayout.addWidget(self.btn_1)
        vlayout.addWidget(self.btn_2)
        vlayout.addWidget(self.btn_3)
        lwg.setLayout(vlayout)

        win_layout.addWidget(lwg)

        #########右控件布局########
        rwg = QWidget() #右边的控件


        rwg1 = QWidget() #定义六个控件作为次级容器, 普通控件->次级布局->次级控件容器（rwg/rwg_com）->右控件布局->右控件容器
        rwg2 = QWidget() 
        rwg3 = QWidget() 
        rwg4 = QWidget()
        rwg5 = QWidget()
        rwg6 = QWidget()
        rwg_com1= QWidget()
        rwg_com2 = QWidget()
        rwg_com3 = QWidget()
        rwg_com4 = QWidget()
        
         
        #串口发送模块的端口选择部分GUI
        rwg_com_layout1 = QHBoxLayout()  #横向布局
        rwg_com_layout1.addWidget(self.s1_lable_com)
        
        rwg_com_layout1.addWidget(self.s1_box_1)
        rwg_com_layout1.addWidget(self.s1_comcheck_btn1)

        rwg_com_layout2 = QHBoxLayout() #横向布局
        rwg_com_layout2.addWidget(self.s1_comopen_btn2)
        rwg_com_layout2.addWidget(self.s1_comclose_btn3)

        rwg_com_layout3 = QHBoxLayout() #横向布局
        rwg_com_layout3.addWidget(self.s1_savedata_btn4)
        rwg_com_layout3.addWidget(self.s1_comclear_btn5)

        rwg_com_layout4 = QHBoxLayout()  #横向布局
        rwg_com_layout4.addWidget(self.s1_comdata_label)
        rwg_com_layout4.addWidget(self.s1_comdata_receive)


        rwg1_hlayout=QHBoxLayout()  #横向布局1
        

        rwg1_hlayout.addWidget(self.s1_box_1)
        rwg1_hlayout.addWidget(self.labLAB_set1)  #添加控件labLAB_set1
        rwg1_hlayout.addWidget(self.L_set_edit)
        rwg1_hlayout.setSizeConstraint(5)

        rwg2_hlayout=QHBoxLayout()   #横向布局2
        rwg2_hlayout.addWidget(self.labLAB_set2)  #添加控件labLAB_set2
        rwg2_hlayout.addWidget(self.A_set_edit) #添加控件


        
        rwg3_hlayout=QHBoxLayout()  #横向布局3
        rwg3_hlayout.addWidget(self.labLAB_set3) #添加控件
        rwg3_hlayout.addWidget(self.B_set_edit) #添加控件
        
        rwg4_hlayout=QHBoxLayout() #横向布局4
        rwg4_hlayout.addWidget(self.x_set_lab)
        rwg4_hlayout.addWidget(self.X_set_edit)
        rwg4_hlayout.addWidget(self.y_set_lab)
        rwg4_hlayout.addWidget(self.Y_set_edit)
        
        rwg5_hlayout=QHBoxLayout() #横向布局5
        rwg5_hlayout.addWidget(self.width_set_lab)
        rwg5_hlayout.addWidget(self.width_set_edit)
        rwg5_hlayout.addWidget(self.height_set_lab)
        rwg5_hlayout.addWidget(self.height_set_edit)

        rwg6_hlayout=QHBoxLayout() #横向布局6    盘符选择
        rwg6_hlayout.addWidget(self.device_lab)
        rwg6_hlayout.addWidget(self.device_combobox)




        rwg1.setLayout(rwg1_hlayout)   #把布局添加到控件
        rwg2.setLayout(rwg2_hlayout)  #把布局添加到控件
        rwg3.setLayout(rwg3_hlayout)
        rwg4.setLayout(rwg4_hlayout)
        rwg5.setLayout(rwg5_hlayout)
        rwg6.setLayout(rwg6_hlayout)
        

        rwg_com1.setLayout(rwg_com_layout1)
        rwg_com2.setLayout(rwg_com_layout2)
        rwg_com3.setLayout(rwg_com_layout3)
        rwg_com4.setLayout(rwg_com_layout4)

        rwg_layout_all = QVBoxLayout()  #设定一个窗体右边的纵向布局。

        rwg_layout_all.addWidget(rwg_com1)
        rwg_layout_all.addWidget(self.com_state_lable)
        rwg_layout_all.addWidget(rwg_com2)
        rwg_layout_all.addWidget(rwg_com4)
      #  rwg_layout_all.addWidget(self.s1_comdata_receive)
        rwg_layout_all.addWidget(rwg1)  #添加控件
        rwg_layout_all.addWidget(rwg2) #添加控件
        rwg_layout_all.addWidget(rwg3) #添加控件
        rwg_layout_all.addWidget(rwg4) #添加控件
        rwg_layout_all.addWidget(rwg5)
        rwg_layout_all.addWidget(rwg6)
        rwg_layout_all.addWidget(rwg_com3)
        

        rwg.setLayout(rwg_layout_all)  #设定控件
        

        win_layout.addWidget(rwg)
     
        self.setLayout(win_layout)
        
        self.ser = serial.Serial()
        self.port_check()
        self.port_imf()
        self.get_disk_device()

        
        ####按钮信号槽#####
        self.btn_1.setCheckable(False)#设置已经被点击
        self.btn_1.clicked.connect(self.btn1State)
        #self.btn_1.clicked.connect(lambda :self.wichBtn(self.btn_1))


        self.btn_2.setEnabled(False)#设置不可用状态
        self.btn_2.clicked.connect(self.btn2State)
        # self.btn_2.clicked.connect(lambda :self.wichBtn(self.btn_2))
        
        self.btn_3.setEnabled(False)
        self.btn_3.clicked.connect(self.btn3State)
     #   self.btn_3.clicked.connect(self.check_frame_buffer_msg)
        self.s1_comcheck_btn1.clicked.connect(self.port_check)
        self.s1_comopen_btn2.clicked.connect(self.port_open)
        self.s1_comclose_btn3.clicked.connect(self.port_close)
        self.s1_box_1.currentTextChanged.connect(self.port_imf)
        self.s1_savedata_btn4.clicked.connect(self.save_lab_roi_data)
        self.s1_comclear_btn5.clicked.connect(self.clear_roi_lab)
        
        

        
    def check_frame_buffer_msg(self):
        while win32gui.FindWindow('pygame','Frame Buffer') != 0 :  #搜索图像传输框，如果存在返回0，发出警告
            check_message = QMessageBox.information(self,"警告","请先关闭图像传输框(Frame Buffer)！",QMessageBox.Yes)


    def btn1State(self):
        if self.btn_1.isEnabled():
        #   print("Btn_1被点击")
            self.btn_2.setEnabled(True)
    
            win32api.ShellExecute(0, 'open', 'transfer_jpg_streaming.exe', 'a', '', 1)           # 前台打开  
        
    def btn2State(self):
        global img
        if self.btn_2.isEnabled():
            self.btn_3.setEnabled(True)
         #   print("Btn_2被点击")
            get_window_jpg()
            cv2.resizeWindow('image',640,480)
            get_image_roi(img_cv)
            lab_data()
       
    
    
    def btn3State(self):
        if self.btn_3.isEnabled():
          #  print("Btn_3被点击")
            RGB_hist_show()
    
    def port_check(self):
        # 检测所有存在的串口，将信息存储在字典中
        self.Com_Dict = {}
        port_list = list(serial.tools.list_ports.comports())
        self.s1_box_1.clear()
        for port in port_list:
            self.Com_Dict["%s" % port[0]] = "%s" % port[1]
            self.s1_box_1.addItem(port[0])
            
        if len(self.Com_Dict) == 0:
            self.com_state_lable.setText("当前串口为:无串口")  
        self.port_imf()

    # 串口信息
    def port_imf(self):
        # 显示选定的串口的详细信息 
        imf_s = self.s1_box_1.currentText()

        if imf_s != "":
            self.com_state_lable.setText("当前串口为:"+str(self.Com_Dict[self.s1_box_1.currentText()]))

    def port_open(self):
        if self.s1_comopen_btn2.isEnabled():
         #   print("open success!")
            self.ser.port = self.s1_box_1.currentText()
            self.ser.baudrate = 115200
            self.ser.bytesize = 8
            self.ser.stopbits = 1
            self.ser.parity = "N"
            self.port_imf()

            try:
                self.ser.open()
            except:
                QMessageBox.critical(self, "Port Error", "此串口不能被打开！")
                return None
                # 打开串口接收定时器，周期为2ms
            self.timer.start(2)
         #   print("set timer successful")

            if self.ser.isOpen():
                self.s1_comopen_btn2.setEnabled(False)
                self.s1_comclose_btn3.setEnabled(True)
                self.s1_savedata_btn4.setEnabled(True)
                self.com_state_lable.setText("串口状态（已开启）")
            

    # 关闭串口
    def port_close(self):
        try:
            self.ser.close()
        except:
            pass
        self.s1_comopen_btn2.setEnabled(True)
        self.s1_comclose_btn3.setEnabled(False)
        # 接收数据和发送数据数目置零
        '''
        self.data_num_received = 0
        self.lineEdit.setText(str(self.data_num_received))
        self.data_num_sended = 0
        self.lineEdit_2.setText(str(self.data_num_sended))
        '''
        self.com_state_lable.setText("串口状态（已关闭）")
 

    # 接收数据
    def data_receive(self):
        try:
            num = self.ser.inWaiting()
        except:
            self.port_close()
            return None
        if num > 0:
            data = self.ser.read(num)
            num = len(data)
            # hex显示
            if False:
            #self.hex_receive.checkState():
                out_s = ''
                for i in range(0, len(data)):
                    out_s = out_s + '{:02X}'.format(data[i]) + ' '
                self.s1_comdata_receive.setText(out_s)
              #  print(out_s)
            else:
                # 串口接收到的字符串为b'123',要转化成unicode字符串才能输出到窗口中去
                self.s1_comdata_receive.setText(data.decode('utf-8'))
              #  print(data.decode('utf-8'))
            # 统计接收字符的数量
       #     self.data_num_received += num
       #     self.lineEdit.setText(str(self.data_num_received))

            # 获取到text光标
           # textCursor = self.s2__receive_text.textCursor()
            # 滚动到底部
           # textCursor.movePosition(textCursor.End)
            # 设置光标到text中去
           # self.s2__receive_text.setTextCursor(textCursor)
        else:
            pass
    def get_disk_device(self):  #获取计算机盘符，添加到下拉框中
        disk = str(psutil.disk_partitions())
        disk_device = r'device'
        for i in re.finditer('device', disk):   
            #print(i.span())
            start = i.span()[1] + 2  #盘符字符串起始位置
            end = i.span()[1] + 4    #盘符字符串终止位置
        #    print(disk[start:end])
            self.device_combobox.addItem(disk[start:end])
    def save_lab_roi_data(self):
        #######将lab编辑框中的内容读取至lab_list#######
        global Lab_list,position_list
        lab_s = str(self.L_set_edit.text())
        where = lab_s.find('-')
       # print(lab_s[0:where])
        Lab_list[0] = float(lab_s[0:where])
        where = where + 1
        Lab_list[1] = float(lab_s[where:len(lab_s)])


        lab_s = str(self.A_set_edit.text())
        if lab_s[0]=='-':
            lab_s=lab_s[1:len(lab_s)]
            where = lab_s.find('-')
            Lab_list[2]= -1 * float(lab_s[0:where])
            if lab_s[where+1] == '-':
                where=where + 2
                Lab_list[3]= -1*float(lab_s[where:len(lab_s)])
            else:
                where = where + 1
                Lab_list[3] = float(lab_s[where:len(lab_s)])
        else:
            where = lab_s.find('-')
            Lab_list[2] = float(lab_s[0:where])
          #  print(lab_s[0:where])
            where = where + 1
            Lab_list[3] = float(lab_s[where:len(lab_s)])
        #    print(lab_s[where:len(lab_s)])

        lab_s = str(self.B_set_edit.text())
        if lab_s[0]=='-':
            lab_s=lab_s[1:len(lab_s)]
            where = lab_s.find('-')
            Lab_list[4]= -1 * float(lab_s[0:where])
            if lab_s[where+1] == '-':
                where=where+2
                Lab_list[5]= -1*float(lab_s[where:len(lab_s)])
            else:
                where = where +1
                Lab_list[5] = float(lab_s[where:len(lab_s)])
        else:
            where = lab_s.find('-')
            Lab_list[4] = float(lab_s[0:where])
          #  print(lab_s[0:where])
            where = where + 1
            Lab_list[5] = float(lab_s[where:len(lab_s)])
         #   print(lab_s[where:len(lab_s)])

     
        #######将roi编辑框中的内容读取至roi_list#######

        roi_s = str(self.X_set_edit.text())
        position_list[0] = int(roi_s)
  

        roi_s = str(self.Y_set_edit.text())
        position_list[1] = int(roi_s)


        roi_s = str(self.width_set_edit.text())
        position_list[2] = int(roi_s)
  
        roi_s = str(self.height_set_edit.text())
        position_list[3] = int(roi_s[0:where])


        
        with open(str(self.device_combobox.currentText())+'\data.txt','w') as data_txt:
            data = str(Lab_list[0])+","+str(Lab_list[1])+","+str(Lab_list[2])+","+str(Lab_list[3])+","+str(Lab_list[4])+","+str(Lab_list[5])            
            data_txt.writelines(data)
            data = str(position_list[0])+","+str(position_list[1])+","+str(position_list[2])+","+str(position_list[3])
            data_txt.writelines('\n')
            data_txt.writelines(data)
    def clear_roi_lab(self):
        global Lab_list,position_list
        for i in range(6):
            Lab_list[i] = 0
         #   print(Lab_list[i])
        for i in range(4):
            position_list[i] = 0
         #   print(position_list[i])
      #  print("clear successful!")
        #重置 lab 标签 、 lab 编辑框 等
        self.LabLAB1.setText("L:"+str(Lab_list[1])+"-"+str(Lab_list[0])+"  X:"+str(position_list[0]))
        self.LabLAB2.setText("A:"+str(Lab_list[3])+"-"+str(Lab_list[2])+"  Y:"+str(position_list[1]))
        self.LabLAB3.setText("B:"+str(Lab_list[5])+"-"+str(Lab_list[4])+"  Width:"+str(position_list[2])+"  Height:"+str(position_list[3]))
        self.L_set_edit.setText(str(Lab_list[1])+"-"+str(Lab_list[0]))
        self.A_set_edit.setText(str(Lab_list[3])+"-"+str(Lab_list[2]))
        self.B_set_edit.setText(str(Lab_list[5])+"-"+str(Lab_list[4]))
        self.X_set_edit.setText(str(position_list[0]))
        self.Y_set_edit.setText(str(position_list[1]))
        self.height_set_edit.setText(str(position_list[3]))
        self.width_set_edit.setText(str(position_list[2]))


         

 


if __name__=="__main__":
    app=QApplication(sys.argv)
    win=WindowClass()
    win.show()
    
    sys.exit(app.exec_())
        

