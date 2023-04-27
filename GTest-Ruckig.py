#!/usr/bin/python3
from kivy.config import Config
Config.set('graphics','width',1000)
Config.set('graphics','height',550)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager,Screen
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy_garden.graph import Graph,MeshLinePlot

from copy import copy
from ruckig import InputParameter, OutputParameter, Result, Ruckig

class Input(Widget):
    def __init__(self, **kwargs):        
        super().__init__(**kwargs)
        self.app = App.get_running_app()

    def on_enter(self):
        self.app.current_position      = float(self.ids['txt_In_Position'].text)
        if abs(float(self.ids['txt_In_Vel'].text)) <= self.app.max_velocity:
            self.app.current_velocity      = float(self.ids['txt_In_Vel'].text)
        else:
            if float(self.ids['txt_In_Vel'].text) > 0:
                self.ids['txt_In_Vel'].text = str(self.app.max_velocity)
                self.app.current_velocity      = float(self.ids['txt_In_Vel'].text)
            else:
                self.ids['txt_In_Vel'].text = str(-self.app.max_velocity)
                self.app.current_velocity      = -float(self.ids['txt_In_Vel'].text)                
        if abs(float(self.ids['txt_In_Acc'].text)) <= self.app.max_acceleration:
            self.app.current_acceleration  = float(self.ids['txt_In_Acc'].text)
        else:
            if float(self.ids['txt_In_Acc'].text) > 0:
                self.ids['txt_In_Acc'].text= str(self.app.max_acceleration)
                self.app.current_acceleration  = float(self.ids['txt_In_Acc'].text)
            else:
                self.ids['txt_In_Acc'].text= str(-self.app.max_acceleration)
                self.app.current_acceleration  = -float(self.ids['txt_In_Acc'].text)                
        self.app.recalculate()


class Output(Widget):
    def __init__(self, **kwargs):        
        super().__init__(**kwargs)
        self.app = App.get_running_app()

    def on_enter(self):
        self.app.target_position      = float(self.ids['txt_Out_Position'].text)
        if abs(float(self.ids['txt_Out_Vel'].text)) <= self.app.max_velocity:
            self.app.target_velocity      = float(self.ids['txt_Out_Vel'].text)
        else:
            if float(self.ids['txt_Out_Vel'].text) > 0:
                self.ids['txt_Out_Vel'].text = str(self.app.max_velocity)
                self.app.target_velocity      = float(self.ids['txt_Out_Vel'].text)
            else:
                self.ids['txt_Out_Vel'].text = str(-self.app.max_velocity)
                self.app.target_velocity      = -float(self.ids['txt_Out_Vel'].text)
        if abs(float(self.ids['txt_Out_Acc'].text)) <= self.app.max_acceleration:
            self.app.target_acceleration  = float(self.ids['txt_Out_Acc'].text)
        else:
            if float(self.ids['txt_Out_Acc'].text) > 0:
                self.ids['txt_Out_Acc'].text= str(self.app.max_acceleration)
                self.app.target_acceleration  = float(self.ids['txt_Out_Acc'].text)
            else:
                self.ids['txt_Out_Acc'].text= str(-self.app.max_acceleration)
                self.app.target_acceleration  = -float(self.ids['txt_Out_Acc'].text)                
        self.app.recalculate()


class Limits(Widget):
    def __init__(self, **kwargs):        
        super().__init__(**kwargs)
        self.app = App.get_running_app()

    def on_enter(self):
        self.app.max_velocity     = float(self.ids['txt_maxVel'].text)
        self.app.max_acceleration = float(self.ids['txt_maxAcc'].text)
        self.app.max_jerk         = float(self.ids['txt_maxJerk'].text)

        self.app.recalculate()


class Screens(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Ww_Graph(Graph):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.xlabel = 'X'
        # self.ylabel = 'Y'
        self.x_ticks_minor = 1
        self.x_ticks_major = 10
        self.y_ticks_major = 10
        self.y_ticks_minor = 1
        self.y_grid_label = True
        self.x_grid_label = True
        self.padding = 5
        self.x_grid = True
        self.y_grid = True
        self.Jerk_plot = MeshLinePlot(color=[1,1,1,0.8])
        self.Acc_plot  = MeshLinePlot(color=[1,0,0,0.8])
        self.Vel_plot  = MeshLinePlot(color=[0,1,0,0.8])
        self.Dist_plot = MeshLinePlot(color=[1,0,1,0.8])
        self.add_plot(self.Jerk_plot)
        self.add_plot(self.Acc_plot)
        self.add_plot(self.Vel_plot)
        self.add_plot(self.Dist_plot)


class Main(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = App.get_running_app()

    def plot(self):
        self.ids['wd_Results'].ids['lbl_DeltaPos'].text = '%.4f'%(self.app.target_position-self.app.current_position)
        self.ids['wd_Results'].ids['lbl_DeltaVel'].text = '%.4f'%(self.app.target_velocity-self.app.current_velocity)
        self.ids['wd_Results'].ids['lbl_DeltaAcc'].text = '%.4f'%(self.app.target_acceleration-self.app.current_acceleration)
        self.ids['wd_Results'].ids['lbl_Duration'].text = '%.4f'%(self.app.first_output.trajectory.duration)
        self.ids['wd_Results'].ids['lbl_CPUTime'].text = '%.4f'%(self.app.first_output.calculation_duration)

        self.ids['gr_Graph'].xmin = 0
        self.ids['gr_Graph'].xmax = self.app.first_output.trajectory.duration
        self.ids['gr_Graph'].ymin = -self.app.inp.max_acceleration[0]-0.5*self.app.inp.max_acceleration[0]
        self.ids['gr_Graph'].ymax =  self.app.inp.target_position[0]+0.005*self.app.inp.target_position[0]
        self.ids['gr_Graph'].Acc_plot.points  = (self.app.Acc_points)
        self.ids['gr_Graph'].Vel_plot.points  = (self.app.Vel_points)        
        self.ids['gr_Graph'].Dist_plot.points = (self.app.Dist_points)


class GTestRuckigApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.Init()

    def Init(self):

        self.otg = Ruckig(1, 0.01)  # DoFs, control cycle
        self.inp = InputParameter(1)
        self.out = OutputParameter(1)

        # Set input parameters
        self.current_position     = 0.0
        self.current_velocity     = 0.0
        self.current_acceleration = 0.0

        self.target_position      = 36.0
        self.target_velocity      = 0.0
        self.target_acceleration  = 0.0

        self.max_velocity         = 6.0
        self.max_acceleration     = 2.0
        self.max_jerk             = 1.0

        self.inp.max_velocity         = [6.0]
        self.inp.max_acceleration     = [2.0]
        self.inp.max_jerk             = [1.0]

        self.inp.current_position     = [self.current_position]
        self.inp.current_velocity     = [self.current_velocity]
        self.inp.current_acceleration = [self.current_acceleration]

        self.inp.target_position      = [self.target_position]
        self.inp.target_velocity      = [self.target_velocity]
        self.inp.target_acceleration  = [self.target_acceleration]

        self.inp.max_velocity         = [self.max_velocity]
        self.inp.max_acceleration     = [self.max_acceleration]
        self.inp.max_jerk             = [self.max_jerk]

        self.Acc_points  = []
        self.Vel_points  = []
        self.Dist_points = []
        
    def recalculate(self):
        self.inp.current_position     = [self.current_position]
        self.inp.current_velocity     = [self.current_velocity]
        self.inp.current_acceleration = [self.current_acceleration]

        self.inp.target_position      = [self.target_position]
        self.inp.target_velocity      = [self.target_velocity]
        self.inp.target_acceleration  = [self.target_acceleration]

        self.inp.max_velocity         = [self.max_velocity]
        self.inp.max_acceleration     = [self.max_acceleration]
        self.inp.max_jerk             = [self.max_jerk]

        self.Acc_points  = []
        self.Vel_points  = []
        self.Dist_points = []

        self.calculate()

    def calculate(self):
        self.first_output, out_list = None, []
        res = Result.Working
        while res == Result.Working:
            res = self.otg.update(self.inp, self.out)
            out_list.append(copy(self.out))

            self.Jerk_points.append((copy(self.out.time),0))
            self.Acc_points.append((copy(self.out.time),copy(self.out.new_acceleration[-1])))
            self.Vel_points.append((copy(self.out.time),copy(self.out.new_velocity[-1])))
            self.Dist_points.append((copy(self.out.time),copy(self.out.new_position[-1])))

            self.out.pass_to_input(self.inp)

            if not self.first_output:
                self.first_output = copy(self.out)

        self.sm.ids['sc_Main'].plot()

    def build(self):
        self.sm = Screens()
        self.calculate()
        return self.sm


if __name__ == '__main__':
    GTestRuckigApp().run()