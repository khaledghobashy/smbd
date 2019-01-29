
import numpy as np
import scipy as sc
from numpy.linalg import multi_dot
from source.cython_definitions.matrix_funcs import A, B, triad as Triad
from scipy.misc import derivative
from numpy import cos, sin

def Mirror(v):
    if v.shape == (1,3):
        return v
    else:
        m = np.array([[1,0,0],[0,-1,0],[0,0,1]],dtype=np.float64)
        return m.dot(v)


class configuration(object):

    def __init__(self):
        self.F_mcr_ver_act = lambda t : 0
        self.J_mcr_ver_act = np.array([[0, 0, 0]],dtype=np.float64)
        self.ax1_jcr_rev = np.array([[0], [0], [0]],dtype=np.float64)
        self.F_jcr_rev = lambda t : 0

        self._set_arguments()

    def _set_arguments(self):
        self.F_mcl_ver_act = self.F_mcr_ver_act
        self.J_mcl_ver_act = Mirror(self.J_mcr_ver_act)
        self.ax1_jcl_rev = Mirror(self.ax1_jcr_rev)
        self.F_jcl_rev = self.F_jcr_rev

    def eval_constants(self):

        c0 = Triad(self.ax1_jcr_rev,)
        c1 = Triad(self.ax1_jcl_rev,)

        self.Mbar_vbr_hub_jcr_rev = multi_dot([A(self.P_vbr_hub).T,c0])
        self.Mbar_vbr_upright_jcr_rev = multi_dot([A(self.P_vbr_upright).T,c0])
        self.Mbar_vbl_hub_jcl_rev = multi_dot([A(self.P_vbl_hub).T,c1])
        self.Mbar_vbl_upright_jcl_rev = multi_dot([A(self.P_vbl_upright).T,c1])



class topology(object):

    def __init__(self,config,prefix=''):
        self.t = 0.0
        self.config = config
        self.prefix = (prefix if prefix=='' else prefix+'.')

        self.n = 0
        self.nrows = 4
        self.ncols = 2*5
        self.rows = np.arange(self.nrows)

        self.jac_rows = np.array([0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3])                        

    
    def _set_mapping(self,indicies_map,interface_map):
        p = self.prefix
    
        self.vbr_upright = indicies_map[interface_map[p+'vbr_upright']]
        self.vbl_upright = indicies_map[interface_map[p+'vbl_upright']]
        self.vbl_hub = indicies_map[interface_map[p+'vbl_hub']]
        self.vbs_ground = indicies_map[interface_map[p+'vbs_ground']]
        self.vbr_hub = indicies_map[interface_map[p+'vbr_hub']]

    def assemble_template(self,indicies_map,interface_map,rows_offset):
        self.rows_offset = rows_offset
        self._set_mapping(indicies_map,interface_map)
        self.rows += self.rows_offset
        self.jac_rows += self.rows_offset
        self.jac_cols = np.array([self.vbs_ground*2,self.vbs_ground*2+1,self.vbr_hub*2,self.vbr_hub*2+1,self.vbs_ground*2,self.vbs_ground*2+1,self.vbl_hub*2,self.vbl_hub*2+1,self.vbr_hub*2,self.vbr_hub*2+1,self.vbr_upright*2,self.vbr_upright*2+1,self.vbl_hub*2,self.vbl_hub*2+1,self.vbl_upright*2,self.vbl_upright*2+1,])

    
    def set_gen_coordinates(self,q):
        pass

    
    def set_gen_velocities(self,qd):
        pass

    
    def eval_pos_eq(self):
        config = self.config
        t = self.t

        x0 = np.eye(1,dtype=np.float64)
        x1 = config.F_jcr_rev(t,)
        x2 = A(self.P_vbr_hub).T
        x3 = A(self.P_vbr_upright)
        x4 = config.Mbar_vbr_upright_jcr_rev[:,0:1]
        x5 = config.F_jcl_rev(t,)
        x6 = A(self.P_vbl_hub).T
        x7 = A(self.P_vbl_upright)
        x8 = config.Mbar_vbl_upright_jcl_rev[:,0:1]

        self.pos_eq_blocks = [-1*config.F_mcr_ver_act(t,) + self.R_vbr_hub[2]*x0,-1*config.F_mcl_ver_act(t,) + self.R_vbl_hub[2]*x0,(cos(x1)*multi_dot([config.Mbar_vbr_hub_jcr_rev[:,1:2].T,x2,x3,x4]) + sin(x1)*-1.0*multi_dot([config.Mbar_vbr_hub_jcr_rev[:,0:1].T,x2,x3,x4])),(cos(x5)*multi_dot([config.Mbar_vbl_hub_jcl_rev[:,1:2].T,x6,x7,x8]) + sin(x5)*-1.0*multi_dot([config.Mbar_vbl_hub_jcl_rev[:,0:1].T,x6,x7,x8]))]

    
    def eval_vel_eq(self):
        config = self.config
        t = self.t

        v0 = np.zeros((1,1),dtype=np.float64)
        v1 = np.eye(1,dtype=np.float64)

        self.vel_eq_blocks = [(v0 + derivative(config.F_mcr_ver_act,t,0.1,1)*-1.0*v1),(v0 + derivative(config.F_mcl_ver_act,t,0.1,1)*-1.0*v1),(v0 + derivative(config.F_jcr_rev,t,0.1,1)*-1.0*v1),(v0 + derivative(config.F_jcl_rev,t,0.1,1)*-1.0*v1)]

    
    def eval_acc_eq(self):
        config = self.config
        t = self.t

        a0 = np.zeros((1,1),dtype=np.float64)
        a1 = np.eye(1,dtype=np.float64)
        a2 = config.F_jcr_rev(t,)
        a3 = config.Mbar_vbr_upright_jcr_rev[:,0:1]
        a4 = self.P_vbr_upright
        a5 = cos(a2)
        a6 = self.Pd_vbr_hub
        a7 = config.Mbar_vbr_hub_jcr_rev[:,1:2]
        a8 = sin(a2)
        a9 = config.Mbar_vbr_hub_jcr_rev[:,0:1]
        a10 = self.P_vbr_hub
        a11 = A(a10).T
        a12 = self.Pd_vbr_upright
        a13 = config.F_jcl_rev(t,)
        a14 = config.Mbar_vbl_upright_jcl_rev[:,0:1]
        a15 = self.P_vbl_upright
        a16 = cos(a13)
        a17 = self.Pd_vbl_hub
        a18 = config.Mbar_vbl_hub_jcl_rev[:,1:2]
        a19 = sin(a13)
        a20 = config.Mbar_vbl_hub_jcl_rev[:,0:1]
        a21 = self.P_vbl_hub
        a22 = A(a21).T
        a23 = self.Pd_vbl_upright

        self.acc_eq_blocks = [(a0 + derivative(config.F_mcr_ver_act,t,0.1,2)*-1.0*a1),(a0 + derivative(config.F_mcl_ver_act,t,0.1,2)*-1.0*a1),(derivative(a2,t,0.1,2)*-1.0*a1 + multi_dot([a3.T,A(a4).T,(a5*B(a6,a7) + a8*-1.0*B(a6,a9)),a6]) + multi_dot([(a5*multi_dot([a7.T,a11]) + a8*-1.0*multi_dot([a9.T,a11])),B(a12,a3),a12]) + 2.0*multi_dot([((a5*multi_dot([B(a10,a7),a6])).T + a8*-1.0*multi_dot([a6.T,B(a10,a9).T])),B(a4,a3),a12])),(derivative(a13,t,0.1,2)*-1.0*a1 + multi_dot([a14.T,A(a15).T,(a16*B(a17,a18) + a19*-1.0*B(a17,a20)),a17]) + multi_dot([(a16*multi_dot([a18.T,a22]) + a19*-1.0*multi_dot([a20.T,a22])),B(a23,a14),a23]) + 2.0*multi_dot([((a16*multi_dot([B(a21,a18),a17])).T + a19*-1.0*multi_dot([a17.T,B(a21,a20).T])),B(a15,a14),a23]))]

    
    def eval_jac_eq(self):
        config = self.config
        t = self.t

        j0 = np.zeros((1,4),dtype=np.float64)
        j1 = np.zeros((1,3),dtype=np.float64)
        j2 = config.Mbar_vbr_upright_jcr_rev[:,0:1]
        j3 = self.P_vbr_upright
        j4 = config.F_jcr_rev(t,)
        j5 = cos(j4)
        j6 = self.P_vbr_hub
        j7 = config.Mbar_vbr_hub_jcr_rev[:,1:2]
        j8 = config.Mbar_vbr_hub_jcr_rev[:,0:1]
        j9 = A(j6).T
        j10 = config.Mbar_vbl_upright_jcl_rev[:,0:1]
        j11 = self.P_vbl_upright
        j12 = config.F_jcl_rev(t,)
        j13 = cos(j12)
        j14 = self.P_vbl_hub
        j15 = config.Mbar_vbl_hub_jcl_rev[:,1:2]
        j16 = config.Mbar_vbl_hub_jcl_rev[:,0:1]
        j17 = A(j14).T

        self.jac_eq_blocks = [config.J_mcr_ver_act,j0,j1,j0,config.J_mcl_ver_act,j0,j1,j0,j1,multi_dot([j2.T,A(j3).T,(j5*B(j6,j7) + sin(j4)*-1.0*B(j6,j8))]),j1,multi_dot([(j5*multi_dot([j7.T,j9]) + sin(j4)*-1.0*multi_dot([j8.T,j9])),B(j3,j2)]),j1,multi_dot([j10.T,A(j11).T,(j13*B(j14,j15) + sin(j12)*-1.0*B(j14,j16))]),j1,multi_dot([(j13*multi_dot([j15.T,j17]) + sin(j12)*-1.0*multi_dot([j16.T,j17])),B(j11,j10)])]
  