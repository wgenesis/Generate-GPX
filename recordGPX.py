#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @File     : recordGPX.py
# @Project  : Sleipnir
# @Software : PyCharm
# @Author   : why
# @Email    : weihaoyuan2@126.com
# @Time     : 2020/8/21 下午4:10

from PyQt5.QtWidgets import QListWidgetItem,QFileDialog
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow,QApplication

from src import myGPX
import sys
import traceback
from src.displayGUI_gpx import *
import time
import math
import re
from geographiclib.geodesic import Geodesic
geod=Geodesic.WGS84

from custom_widgets.my_port import *
from custom_widgets.slide_message import *
from custom_widgets.switch_button import *

class GpsInfo():
    def __init__(self):
        self.lat=None
        self.lon=None
        self.altitude=None
        self.velocity=None
        self.status=None
        self.heading=None
        self.pitch=None
        self.roll=None
        self.satenum=None
        self.timestamp=None

class MyWindows(QMainWindow,Ui_MainWindow):
    def __init__(self,parent=None):
        super(MyWindows, self).__init__(parent)
        self.gps_info=GpsInfo()
        self.setupUi(self)
        self.retranslateUi(self)
        self.gpx=myGPX.Gpx()
        self.set_subwin_enabled(False)
        self.metadata.setEnabled(False)
        self.message=Message(geometry=(0, 790, 1136, 30),parent=self.centralwidget)
        self.wpt_number=1
        self.rte_number={}
        self.rte_wpt_list={}
        self.trk_number={}
        self.trk_trkseg_number={}
        self.record_interval_type='time'
        self.open_port = SwitchBtn(geometry=(520, 58, 60, 25), parent=self.centralwidget)
        self.my_port=GPSPort(self)
        self.port_update = QTimer()
        self.port_update.timeout.connect(self.my_port.updatePort)
        self.port_update.start(500)
        self.record_trk=QTimer()
        self.record_trk.timeout.connect(self.record_trk_event)
        self.set_all_enabled(False)
        self.last_coordinate=False
        self.trk_extensions_attribute={'速  度':False,'状  态':False,'时间戳':False,
                                   '航向角':False,'俯仰角':False,'翻滚角':False}
        self.chinese_to_english={'速  度':'velocity','状  态':'status','时间戳':'timestamp',
                                   '航向角':'heading','俯仰角':'pitch','翻滚角':'roll'}

    def all_clear(self):
        self.last_coordinate=False
        self.record_trk.stop()
        self.gpx=myGPX.Gpx()
        self.wpt_number=1
        self.rte_number.clear()
        self.rte_wpt_list.clear()
        self.trk_number.clear()
        self.metadata_desc_text.clear()
        self.metadata_name_text.clear()
        self.wpt_name_text.clear()
        self.wpt_desc_text.clear()
        self.wpt_list_display.clear()
        self.rte_name_text.clear()
        self.rte_desc_text.clear()
        self.rte_select_list.clear()
        self.rte_wpt_list_display.clear()
        self.rte_wpt_name_text.clear()
        self.rte_wpt_desc_text.clear()
        self.trk_name_text.clear()
        self.trk_desc_text.clear()
        self.trk_trkseg_number.clear()
        self.trk_select_list.clear()
        self.set_all_enabled(False)
        self.metadata_author_text.clear()
        if self.my_port.portOpen:
            self.begin.setEnabled(True)


    def set_subwin_enabled(self,Bool):
        self.wpt.setEnabled(Bool)
        self.rte.setEnabled(Bool)
        self.trk.setEnabled(Bool)

    def init_ui(self):
        self.begin.clicked.connect(self.gpx_event)
        self.metadata_create.clicked.connect(self.metadata_event)
        self.print_gpx.clicked.connect(self.print_gpx_slot_function)
        self.wpt_add_wpt.clicked.connect(self.wpt_event)
        self.rte_add_rte.clicked.connect(self.rte_event)
        self.rte_select_list.currentIndexChanged.connect(self.rte_elect_event)
        self.rte_add_rte_wpt.clicked.connect(self.rte_event)
        self.my_port.availablePortSig.connect(self.update_available_port_sig)
        self.my_port.portOpenSig.connect(self.open_port.statusSwitch)
        self.port_select_list.currentTextChanged.connect(self.port_change_event)
        self.open_port.checkedChanged.connect(self.switch_port)
        self.my_port.gpsDataSig.connect(self.read_port)
        self.add_trk.clicked.connect(self.trk_add_event)
        self.trk_begin.clicked.connect(self.trk_event)
        self.trk_extensions_pitch.clicked.connect(self.trk_extensions_event)
        self.trk_extensions_roll.clicked.connect(self.trk_extensions_event)
        self.trk_extensions_heading.clicked.connect(self.trk_extensions_event)
        self.trk_extensions_status.clicked.connect(self.trk_extensions_event)
        self.trk_extensions_velocity.clicked.connect(self.trk_extensions_event)
        self.trk_extensions_time_stamp.clicked.connect(self.trk_extensions_event)
        self.trk_pause.clicked.connect(self.trk_event)
        self.trk_cancel.clicked.connect(self.trk_event)
        self.trk_select_list.currentIndexChanged.connect(self.trk_select_event)
        self.stop.clicked.connect(self.gpx_event)
        self.cancel.clicked.connect(self.gpx_event)
        self.export_gpx.clicked.connect(self.gpx_event)

    def trk_extensions_event(self):
        sender=self.sender()
        self.trk_extensions_attribute[sender.text()]=sender.isChecked()

    def gps_info_display(self):
        self.info_lat_text.setText(str(self.gps_info.lat))
        self.info_lon_text.setText(str(self.gps_info.lon))
        self.info_altitude_text.setText(str(self.gps_info.altitude))
        self.info_velocity_text.setText(str(self.gps_info.velocity))
        self.info_status_text.setText(self.gps_info.status)
        self.info_heading_text.setText(str(self.gps_info.heading))
        self.info_pitch_text.setText(str(self.gps_info.pitch))
        self.info_roll_text.setText(str(self.gps_info.roll))
        self.info_satellite_number_text.setText(str(self.gps_info.satenum))
        self.info_time_stamp_text.setText(str(self.gps_info.timestamp)[-7:])

    def read_port(self,data):
        try:
            if len(data) and ',' in data:
                GPFPD_split_list = data.split(',')
                if len(GPFPD_split_list) > 15:
                    self.gps_info.gpstime = int(float(GPFPD_split_list[2]))
                    self.gps_info.heading = float(GPFPD_split_list[3])
                    self.gps_info.pitch = float(GPFPD_split_list[4])
                    self.gps_info.roll = float(GPFPD_split_list[5])
                    self.gps_info.lat = float(GPFPD_split_list[6])
                    self.gps_info.lon = float(GPFPD_split_list[7])
                    self.gps_info.altitude = float(GPFPD_split_list[8])
                    ve = float(GPFPD_split_list[9])
                    vs = float(GPFPD_split_list[10])
                    NSV1 = int(GPFPD_split_list[13])
                    NSV2 = int(GPFPD_split_list[14])
                    status_str_list = GPFPD_split_list[15].split('*')

                    self.gps_info.velocity = format(math.sqrt(ve ** 2 + vs ** 2),'0.3f')

                    status = status_str_list[0]
                    if status == '0B' or status == '4B':
                        self.gps_info.status = 'good'
                    elif status == '05' or status == '45':
                        self.gps_info.status = 'normal'
                    else:
                        self.gps_info.status = 'bad'
                    self.gps_info.satenum = int(NSV1 + NSV2) / 2
                    self.gps_info.timestamp = int(time.time() * 1000)
                    self.gps_info_display()
        except:
                pass

    def switch_port(self):
        if self.my_port.portOpen == False:
            selectPortIndex=self.port_select_list.currentIndex()
            baudrate=self.port_select_baudrate_list.currentText()
            portConfig={'portIndex':selectPortIndex,'baudrate':baudrate,'stopbits':'1','parity':'none'}
            if self.my_port.openPort(portConfig):
                self.my_port.portOpen = True
                self.begin.setEnabled(True)
                self.message.setStatusMessage('端口打开成功', 'green', 'white')
            else:
                self.message.setStatusMessage('端口打开失败！','red','white')
                self.open_port.statusSwitch(False)
        elif self.my_port.portOpen==True:
            self.my_port.closePort()
            self.message.setStatusMessage('端口关闭成功', 'green', 'white')

    def set_all_enabled(self,Bool):
        self.begin.setEnabled(Bool)
        self.stop.setEnabled(Bool)
        self.cancel.setEnabled(Bool)
        self.print_gpx.setEnabled(Bool)
        self.export_gpx.setEnabled(Bool)
        self.metadata.setEnabled(Bool)
        self.set_subwin_enabled(Bool)

    def port_change_event(self):
        self.open_port.statusSwitch(False)
        self.my_port.closePort()

    def update_available_port_sig(self,ports):
        self.message.setStatusMessage('端口更新', 'orange', 'white')
        self.port_select_list.clear()
        self.port_select_list.addItems(ports)

    def print_gpx_slot_function(self):
        self.gpx.print_xml()

    def metadata_event(self):
        can_create=True
        if len(self.metadata_name_text.text()):
            self.gpx.metadata.name = self.metadata_name_text.text()
        else:
            can_create=False
            self.message.setStatusMessage('生成失败,请输入名称', 'red', 'white')
        if len(self.metadata_desc_text.text()):
            self.gpx.metadata.desc = self.metadata_desc_text.text()
        else:
            can_create=False
            self.message.setStatusMessage('生成失败,请输入描述', 'red', 'white')
        if len(self.metadata_author_text.text()):
            self.gpx.metadata.author.name=self.metadata_author_text.text()
        if can_create:
            self.gpx.update_metadata()
            self.message.setStatusMessage('元数据生成成功','green','white')
            self.metadata.setEnabled(False)
            self.print_gpx.setEnabled(True)
            self.export_gpx.setEnabled(True)
            self.set_subwin_enabled(True)

    def gpx_event(self):
        sender=self.sender()
        if sender.text()=='开始':
            self.gpx=myGPX.Gpx()
            self.begin.setEnabled(False)
            self.metadata.setEnabled(True)
            self.stop.setEnabled(True)
            self.cancel.setEnabled(True)
        if sender.text()=='停止':
            save_gpx_file_path = QFileDialog.getSaveFileName(self, '保存GPX', '*.gpx')[0]
            try:
                self.gpx.export_gpx(save_gpx_file_path)
                self.message.setStatusMessage('保存成功','green','white')
            except:
                self.message.setStatusMessage('保存失败', 'red', 'white')
            self.all_clear()
        if sender.text()=='取消':
            self.all_clear()
        if sender.text()=='导出GPX':
            try:
                save_gpx_file_path = QFileDialog.getSaveFileName(self, '保存GPX', '*.gpx')[0]
                self.record_trk.stop()
                self.trk_begin.setEnabled(True)
                self.set_trk_wpt_status(True)
                self.gpx.export_gpx(save_gpx_file_path)
                self.message.setStatusMessage('保存成功', 'green', 'white')
            except:
                self.message.setStatusMessage('保存失败','red','white')

    def wpt_event(self):
        can_create = True
        wpt=myGPX.Wpt()
        wpt.lat=self.gps_info.lat
        wpt.lon=self.gps_info.lon
        if len(self.wpt_name_text.text()):
            wpt.name = self.wpt_name_text.text()
        else:
            can_create = False
            self.message.setStatusMessage('航路点添加失败,请输入名称', 'red', 'white')
        if len(self.wpt_desc_text.text()):
            wpt.desc = self.wpt_desc_text.text()
        else:
            can_create = False
            self.message.setStatusMessage('航路点添加失败,请输入描述', 'red', 'white')
        if can_create:
            try:
                self.gpx.add_waypoint(wpt)
                item = QListWidgetItem('{}.'.format(self.wpt_number) + wpt.name + '({})'.format(wpt.desc))
                self.wpt_number += 1
                self.wpt_list_display.addItem(item)
                self.message.setStatusMessage('航路点添加成功', 'green', 'white')
            except Exception as e:
                self.message.setStatusMessage('航路点添加失败:'+traceback.format_exc().split('\n')[-2], 'red', 'white')

    def rte_elect_event(self):
        self.rte_wpt_name_text.clear()
        self.rte_wpt_desc_text.clear()
        self.rte_wpt_list_display.clear()
        if self.rte_select_list.currentData() is not None:
            self.rte_wpt_list_display.addItems(self.rte_wpt_list[self.rte_select_list.currentData()])

    def rte_event(self):
        sender=self.sender()
        can_create = True
        if sender.text() == '添加航迹':
            rte = myGPX.Rte()
            if len(self.rte_name_text.text()):
                rte.name = self.rte_name_text.text()
            else:
                can_create = False
                self.message.setStatusMessage('航迹添加失败,请输入名称', 'red', 'white')
            if len(self.rte_desc_text.text()):
                rte.desc = self.rte_desc_text.text()
            else:
                can_create = False
                self.message.setStatusMessage('航迹添加失败,请输入描述', 'red', 'white')
            if can_create:
                try:
                    self.gpx.add_route(rte)
                    self.rte_number[rte.name]=1
                    self.rte_wpt_list[rte.name]=[]
                    self.rte_select_list.addItem(rte.name + '({})'.format(rte.desc),userData=rte.name)
                    self.message.setStatusMessage('航迹添加成功', 'green', 'white')
                except Exception as e:
                    self.message.setStatusMessage('航迹添加失败:' + traceback.format_exc().split('\n')[-2], 'red', 'white')
        if sender.text()=='添加航迹点':
            rte_name=self.rte_select_list.currentData()
            if rte_name is None:
                self.message.setStatusMessage('添加失败,请先选择航迹','red','white')
            else:
                wpt = myGPX.Wpt()
                wpt.lat=self.gps_info.lat
                wpt.lon=self.gps_info.lon
                if len(self.rte_wpt_name_text.text()):
                    wpt.name = self.rte_wpt_name_text.text()
                else:
                    can_create = False
                    self.message.setStatusMessage('航迹点添加失败,请输入名称', 'red', 'white')
                if len(self.rte_desc_text.text()):
                    wpt.desc = self.rte_wpt_desc_text.text()
                else:
                    can_create = False
                    self.message.setStatusMessage('航迹点添加失败,请输入描述', 'red', 'white')
                if can_create:
                    try:
                        self.gpx.add_route_waypoint(rte_name,wpt)
                        self.rte_wpt_list[rte_name].append('{}.'.format(self.rte_number[rte_name]) + wpt.name + '({})'.format(wpt.desc))
                        item = QListWidgetItem('{}.'.format(self.rte_number[rte_name]) + wpt.name + '({})'.format(wpt.desc))
                        self.rte_number[rte_name]+=1
                        self.rte_wpt_list_display.addItem(item)
                        self.message.setStatusMessage('航迹点添加成功', 'green', 'white')
                    except Exception as e:
                        self.message.setStatusMessage('航迹点添加失败:' + traceback.format_exc().split('\n')[-2], 'red','white')

    def trk_add_event(self):
        can_create = True
        trk = myGPX.Trk()
        if len(self.trk_name_text.text()):
            trk.name = self.trk_name_text.text()
        else:
            can_create = False
            self.message.setStatusMessage('轨迹添加失败,请输入名称', 'red', 'white')
        if len(self.trk_desc_text.text()):
            trk.desc = self.trk_desc_text.text()
        else:
            can_create = False
            self.message.setStatusMessage('轨迹添加失败,请输入描述', 'red', 'white')
        if can_create:
            try:
                self.gpx.add_track(trk)
                self.trk_trkseg_number[trk.name] = 0
                self.trk_select_list.addItem(trk.name + '({})'.format(trk.desc), userData=trk.name)
                self.message.setStatusMessage('轨迹添加成功', 'green', 'white')
            except Exception as e:
                self.message.setStatusMessage('轨迹添加失败:' + traceback.format_exc().split('\n')[-2], 'red','white')

    def set_trk_wpt_status(self,Bool):
        self.trk_record_interval.setEnabled(Bool)
        self.trk_extensions.setEnabled(Bool)
        self.trk_select_list.setEnabled(Bool)

    def record_trk_event(self):
        if self.trk_record_interval_dis.isChecked():
            if not self.last_coordinate:
                self.last_coordinate=[self.gps_info.lat,self.gps_info.lon]
            else:
                dis=geod.Inverse(self.last_coordinate[0],self.last_coordinate[1],self.gps_info.lat,self.gps_info.lon)
                if dis['s12'] >=float(self.trk_record_interval_dis_set.text()):
                    wpt=myGPX.Wpt()
                    wpt.lat=self.gps_info.lat
                    wpt.lon=self.gps_info.lon
                    if self.trk_extensions_time.isChecked():
                        wpt.set_time()
                    if self.trk_extensions_altitude.isChecked():
                        wpt.ele=self.gps_info.altitude
                    Dict = {}
                    for key, value in self.trk_extensions_attribute.items():
                        if value:
                            Dict[self.chinese_to_english[key]] = eval('self.gps_info.{}'.format(self.chinese_to_english[key]))
                    self.last_coordinate = [self.gps_info.lat, self.gps_info.lon]
                    element = self.gpx.add_track_waypoint(self.trk_select_list.currentData(), wpt)
                    self.trk_count_number.setText(str(self.trk_trkseg_number[self.trk_select_list.currentData()]))
                    self.trk_trkseg_number[self.trk_select_list.currentData()] += 1
                    if len(Dict):
                        extensions=myGPX.Extensions(Dict)
                        myGPX.add_extensions(element, 'extensions', extensions)

        elif self.trk_record_interval_time.isChecked():
            wpt = myGPX.Wpt()
            wpt.lat = self.gps_info.lat
            wpt.lon = self.gps_info.lon
            if self.trk_extensions_time.isChecked():
                wpt.set_time()
            if self.trk_extensions_altitude.isChecked():
                wpt.ele = self.gps_info.altitude
            Dict = {}
            for key, value in self.trk_extensions_attribute.items():
                if value:
                    Dict[self.chinese_to_english[key]] = eval('self.gps_info.{}'.format(self.chinese_to_english[key]))
            element = self.gpx.add_track_waypoint(self.trk_select_list.currentData(), wpt)
            self.trk_count_number.setText(str(self.trk_trkseg_number[self.trk_select_list.currentData()]))
            self.trk_trkseg_number[self.trk_select_list.currentData()] += 1
            if len(Dict):
                extensions = myGPX.Extensions(Dict)
                myGPX.add_extensions(element, 'extensions', extensions)

    def trk_event(self):
        sender=self.sender()
        if sender.text()=='开始' :
            trk_name = self.trk_select_list.currentData()
            if trk_name is None:
                self.message.setStatusMessage('开始失败,请先选择轨迹', 'red', 'white')
            else:
                self.trk_begin.setEnabled(False)
                self.set_trk_wpt_status(False)
                if self.trk_record_interval_time.isChecked():
                    self.record_trk.start(float(self.trk_record_interval_time_set.text())*1000)
                if self.trk_record_interval_dis.isChecked():
                    self.record_trk.start(1)
        if sender.text()=='暂停':
            self.trk_begin.setEnabled(True)
            self.set_trk_wpt_status(True)
            self.record_trk.stop()
        if sender.text()=='取消':
            self.gpx.remove_track_trkseg(self.trk_select_list.currentData())
            self.trk_trkseg_number[self.trk_select_list.currentData()] = 0
            self.record_trk.stop()
            self.trk_count_number.setText(str(self.trk_trkseg_number[self.trk_select_list.currentData()]))

    def trk_select_event(self):
        if len(self.trk_trkseg_number):
            self.trk_count_number.setText(str(self.trk_trkseg_number[self.trk_select_list.currentData()]))
        else:
            self.trk_count_number.setText(str(0))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin=MyWindows()
    myWin.init_ui()
    myWin.show()
    app.exec_()
    sys.exit(0)