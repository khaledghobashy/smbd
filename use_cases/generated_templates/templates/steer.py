
import os
import numpy as np
import pandas as pd
from scipy.misc import derivative
from numpy import cos, sin
from numpy.linalg import multi_dot
from source.cython_definitions.matrix_funcs import A, B, G, E, triad, skew_matrix as skew
from source.solvers.py_numerical_functions import mirrored



path = os.path.dirname(__file__)

class configuration(object):

    def __init__(self):
        self.R_rbs_coupler = np.array([[0], [0], [0]],dtype=np.float64)
        self.P_rbs_coupler = np.array([[0], [0], [0], [0]],dtype=np.float64)
        self.Rd_rbs_coupler = np.array([[0], [0], [0]],dtype=np.float64)
        self.Pd_rbs_coupler = np.array([[0], [0], [0], [0]],dtype=np.float64)
        self.Rdd_rbs_coupler = np.array([[0], [0], [0]],dtype=np.float64)
        self.Pdd_rbs_coupler = np.array([[0], [0], [0], [0]],dtype=np.float64)
        self.m_rbs_coupler = 1
        self.Jbar_rbs_coupler = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]],dtype=np.float64)
        self.R_rbr_rocker = np.array([[0], [0], [0]],dtype=np.float64)
        self.P_rbr_rocker = np.array([[0], [0], [0], [0]],dtype=np.float64)
        self.Rd_rbr_rocker = np.array([[0], [0], [0]],dtype=np.float64)
        self.Pd_rbr_rocker = np.array([[0], [0], [0], [0]],dtype=np.float64)
        self.Rdd_rbr_rocker = np.array([[0], [0], [0]],dtype=np.float64)
        self.Pdd_rbr_rocker = np.array([[0], [0], [0], [0]],dtype=np.float64)
        self.m_rbr_rocker = 1
        self.Jbar_rbr_rocker = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]],dtype=np.float64)
        self.ax1_jcr_rocker_ch = np.array([[0], [0], [0]],dtype=np.float64)
        self.pt1_jcr_rocker_ch = np.array([[0], [0], [0]],dtype=np.float64)
        self.ax1_jcs_rc_sph = np.array([[0], [0], [0]],dtype=np.float64)
        self.pt1_jcs_rc_sph = np.array([[0], [0], [0]],dtype=np.float64)
        self.ax1_jcs_rc_cyl = np.array([[0], [0], [0]],dtype=np.float64)
        self.pt1_jcs_rc_cyl = np.array([[0], [0], [0]],dtype=np.float64)                       

    
    @property
    def q(self):
        q = np.concatenate([self.R_rbs_coupler,self.P_rbs_coupler,self.R_rbr_rocker,self.P_rbr_rocker,self.R_rbl_rocker,self.P_rbl_rocker])
        return q

    @property
    def qd(self):
        qd = np.concatenate([self.Rd_rbs_coupler,self.Pd_rbs_coupler,self.Rd_rbr_rocker,self.Pd_rbr_rocker,self.Rd_rbl_rocker,self.Pd_rbl_rocker])
        return qd

    def load_from_csv(self,csv_file):
        file_path = os.path.join(path,csv_file)
        dataframe = pd.read_csv(file_path,index_col=0)
        for ind in dataframe.index:
            shape = getattr(self,ind).shape
            v = np.array(dataframe.loc[ind],dtype=np.float64)
            v = np.resize(v,shape)
            setattr(self,ind,v)
        self._set_arguments()

    def _set_arguments(self):
        self.R_rbl_rocker = mirrored(self.R_rbr_rocker)
        self.P_rbl_rocker = mirrored(self.P_rbr_rocker)
        self.Rd_rbl_rocker = mirrored(self.Rd_rbr_rocker)
        self.Pd_rbl_rocker = mirrored(self.Pd_rbr_rocker)
        self.Rdd_rbl_rocker = mirrored(self.Rdd_rbr_rocker)
        self.Pdd_rbl_rocker = mirrored(self.Pdd_rbr_rocker)
        self.m_rbl_rocker = self.m_rbr_rocker
        self.Jbar_rbl_rocker = mirrored(self.Jbar_rbr_rocker)
        self.ax1_jcl_rocker_ch = mirrored(self.ax1_jcr_rocker_ch)
        self.pt1_jcl_rocker_ch = mirrored(self.pt1_jcr_rocker_ch)
    




class topology(object):

    def __init__(self,prefix='',cfg=None):
        self.t = 0.0
        self.config = (configuration() if cfg is None else cfg)
        self.prefix = (prefix if prefix=='' else prefix+'.')

        self.n  = 21
        self.nc = 20
        self.nrows = 14
        self.ncols = 2*5
        self.rows = np.arange(self.nrows)

        self.jac_rows = np.array([0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,8,8,8,8,9,9,9,9,10,10,10,10,11,12,13])
        self.joints_reactions_indicies = ['F_rbr_rocker_jcr_rocker_ch','T_rbr_rocker_jcr_rocker_ch','F_rbr_rocker_jcs_rc_sph','T_rbr_rocker_jcs_rc_sph','F_rbl_rocker_jcl_rocker_ch','T_rbl_rocker_jcl_rocker_ch','F_rbl_rocker_jcs_rc_cyl','T_rbl_rocker_jcs_rc_cyl']

    
    def _set_mapping(self,indicies_map,interface_map):
        p = self.prefix
        self.rbs_coupler = indicies_map[p+'rbs_coupler']
        self.rbr_rocker = indicies_map[p+'rbr_rocker']
        self.rbl_rocker = indicies_map[p+'rbl_rocker']
        self.vbs_ground = indicies_map[interface_map[p+'vbs_ground']]
        self.vbs_chassis = indicies_map[interface_map[p+'vbs_chassis']]

    def assemble_template(self,indicies_map,interface_map,rows_offset):
        self.rows_offset = rows_offset
        self._set_mapping(indicies_map,interface_map)
        self.rows += self.rows_offset
        self.jac_rows += self.rows_offset
        self.jac_cols = np.array([self.rbr_rocker*2,self.rbr_rocker*2+1,self.vbs_chassis*2,self.vbs_chassis*2+1,self.rbr_rocker*2,self.rbr_rocker*2+1,self.vbs_chassis*2,self.vbs_chassis*2+1,self.rbr_rocker*2,self.rbr_rocker*2+1,self.vbs_chassis*2,self.vbs_chassis*2+1,self.rbs_coupler*2,self.rbs_coupler*2+1,self.rbr_rocker*2,self.rbr_rocker*2+1,self.rbl_rocker*2,self.rbl_rocker*2+1,self.vbs_chassis*2,self.vbs_chassis*2+1,self.rbl_rocker*2,self.rbl_rocker*2+1,self.vbs_chassis*2,self.vbs_chassis*2+1,self.rbl_rocker*2,self.rbl_rocker*2+1,self.vbs_chassis*2,self.vbs_chassis*2+1,self.rbs_coupler*2,self.rbs_coupler*2+1,self.rbl_rocker*2,self.rbl_rocker*2+1,self.rbs_coupler*2,self.rbs_coupler*2+1,self.rbl_rocker*2,self.rbl_rocker*2+1,self.rbs_coupler*2,self.rbs_coupler*2+1,self.rbl_rocker*2,self.rbl_rocker*2+1,self.rbs_coupler*2,self.rbs_coupler*2+1,self.rbl_rocker*2,self.rbl_rocker*2+1,self.rbs_coupler*2+1,self.rbr_rocker*2+1,self.rbl_rocker*2+1])

    def set_initial_states(self):
        self.set_gen_coordinates(self.config.q)
        self.set_gen_velocities(self.config.qd)

    
    def eval_constants(self):
        config = self.config

        self.F_rbs_coupler_gravity = np.array([[0], [0], [9810.0*config.m_rbs_coupler]],dtype=np.float64)
        self.F_rbr_rocker_gravity = np.array([[0], [0], [9810.0*config.m_rbr_rocker]],dtype=np.float64)
        self.F_rbl_rocker_gravity = np.array([[0], [0], [9810.0*config.m_rbl_rocker]],dtype=np.float64)

        c0 = A(config.P_rbr_rocker).T
        c1 = triad(config.ax1_jcr_rocker_ch)
        c2 = A(config.P_vbs_chassis).T
        c3 = config.pt1_jcr_rocker_ch
        c4 = -1*multi_dot([c0,config.R_rbr_rocker])
        c5 = -1*multi_dot([c2,config.R_vbs_chassis])
        c6 = triad(config.ax1_jcs_rc_sph)
        c7 = A(config.P_rbs_coupler).T
        c8 = config.pt1_jcs_rc_sph
        c9 = -1*multi_dot([c7,config.R_rbs_coupler])
        c10 = A(config.P_rbl_rocker).T
        c11 = triad(config.ax1_jcl_rocker_ch)
        c12 = config.pt1_jcl_rocker_ch
        c13 = -1*multi_dot([c10,config.R_rbl_rocker])
        c14 = triad(config.ax1_jcs_rc_cyl)
        c15 = config.pt1_jcs_rc_cyl

        self.Mbar_rbr_rocker_jcr_rocker_ch = multi_dot([c0,c1])
        self.Mbar_vbs_chassis_jcr_rocker_ch = multi_dot([c2,c1])
        self.ubar_rbr_rocker_jcr_rocker_ch = (multi_dot([c0,c3]) + c4)
        self.ubar_vbs_chassis_jcr_rocker_ch = (multi_dot([c2,c3]) + c5)
        self.Mbar_rbr_rocker_jcs_rc_sph = multi_dot([c0,c6])
        self.Mbar_rbs_coupler_jcs_rc_sph = multi_dot([c7,c6])
        self.ubar_rbr_rocker_jcs_rc_sph = (multi_dot([c0,c8]) + c4)
        self.ubar_rbs_coupler_jcs_rc_sph = (multi_dot([c7,c8]) + c9)
        self.Mbar_rbl_rocker_jcl_rocker_ch = multi_dot([c10,c11])
        self.Mbar_vbs_chassis_jcl_rocker_ch = multi_dot([c2,c11])
        self.ubar_rbl_rocker_jcl_rocker_ch = (multi_dot([c10,c12]) + c13)
        self.ubar_vbs_chassis_jcl_rocker_ch = (multi_dot([c2,c12]) + c5)
        self.Mbar_rbl_rocker_jcs_rc_cyl = multi_dot([c10,c14])
        self.Mbar_rbs_coupler_jcs_rc_cyl = multi_dot([c7,c14])
        self.ubar_rbl_rocker_jcs_rc_cyl = (multi_dot([c10,c15]) + c13)
        self.ubar_rbs_coupler_jcs_rc_cyl = (multi_dot([c7,c15]) + c9)

    
    def set_gen_coordinates(self,q):
        self.R_rbs_coupler = q[0:3,0:1]
        self.P_rbs_coupler = q[3:7,0:1]
        self.R_rbr_rocker = q[7:10,0:1]
        self.P_rbr_rocker = q[10:14,0:1]
        self.R_rbl_rocker = q[14:17,0:1]
        self.P_rbl_rocker = q[17:21,0:1]

    
    def set_gen_velocities(self,qd):
        self.Rd_rbs_coupler = qd[0:3,0:1]
        self.Pd_rbs_coupler = qd[3:7,0:1]
        self.Rd_rbr_rocker = qd[7:10,0:1]
        self.Pd_rbr_rocker = qd[10:14,0:1]
        self.Rd_rbl_rocker = qd[14:17,0:1]
        self.Pd_rbl_rocker = qd[17:21,0:1]

    
    def set_gen_accelerations(self,qdd):
        self.Rdd_rbs_coupler = qdd[0:3,0:1]
        self.Pdd_rbs_coupler = qdd[3:7,0:1]
        self.Rdd_rbr_rocker = qdd[7:10,0:1]
        self.Pdd_rbr_rocker = qdd[10:14,0:1]
        self.Rdd_rbl_rocker = qdd[14:17,0:1]
        self.Pdd_rbl_rocker = qdd[17:21,0:1]

    
    def set_lagrange_multipliers(self,Lambda):
        self.L_jcr_rocker_ch = Lambda[0:5,0:1]
        self.L_jcs_rc_sph = Lambda[5:8,0:1]
        self.L_jcl_rocker_ch = Lambda[8:13,0:1]
        self.L_jcs_rc_cyl = Lambda[13:17,0:1]

    
    def eval_pos_eq(self):
        config = self.config
        t = self.t

        x0 = self.R_rbr_rocker
        x1 = -1*self.R_vbs_chassis
        x2 = self.P_rbr_rocker
        x3 = A(x2)
        x4 = A(self.P_vbs_chassis)
        x5 = x3.T
        x6 = self.Mbar_vbs_chassis_jcr_rocker_ch[:,2:3]
        x7 = -1*self.R_rbs_coupler
        x8 = self.P_rbs_coupler
        x9 = A(x8)
        x10 = self.R_rbl_rocker
        x11 = self.P_rbl_rocker
        x12 = A(x11)
        x13 = x12.T
        x14 = self.Mbar_vbs_chassis_jcl_rocker_ch[:,2:3]
        x15 = self.Mbar_rbl_rocker_jcs_rc_cyl[:,0:1].T
        x16 = self.Mbar_rbs_coupler_jcs_rc_cyl[:,2:3]
        x17 = self.Mbar_rbl_rocker_jcs_rc_cyl[:,1:2].T
        x18 = (x10 + x7 + multi_dot([x12,self.ubar_rbl_rocker_jcs_rc_cyl]) + -1*multi_dot([x9,self.ubar_rbs_coupler_jcs_rc_cyl]))
        x19 = -1*np.eye(1,dtype=np.float64)

        self.pos_eq_blocks = [(x0 + x1 + multi_dot([x3,self.ubar_rbr_rocker_jcr_rocker_ch]) + -1*multi_dot([x4,self.ubar_vbs_chassis_jcr_rocker_ch])),multi_dot([self.Mbar_rbr_rocker_jcr_rocker_ch[:,0:1].T,x5,x4,x6]),multi_dot([self.Mbar_rbr_rocker_jcr_rocker_ch[:,1:2].T,x5,x4,x6]),(x0 + x7 + multi_dot([x3,self.ubar_rbr_rocker_jcs_rc_sph]) + -1*multi_dot([x9,self.ubar_rbs_coupler_jcs_rc_sph])),(x10 + x1 + multi_dot([x12,self.ubar_rbl_rocker_jcl_rocker_ch]) + -1*multi_dot([x4,self.ubar_vbs_chassis_jcl_rocker_ch])),multi_dot([self.Mbar_rbl_rocker_jcl_rocker_ch[:,0:1].T,x13,x4,x14]),multi_dot([self.Mbar_rbl_rocker_jcl_rocker_ch[:,1:2].T,x13,x4,x14]),multi_dot([x15,x13,x9,x16]),multi_dot([x17,x13,x9,x16]),multi_dot([x15,x13,x18]),multi_dot([x17,x13,x18]),(x19 + (multi_dot([x8.T,x8]))**(1.0/2.0)),(x19 + (multi_dot([x2.T,x2]))**(1.0/2.0)),(x19 + (multi_dot([x11.T,x11]))**(1.0/2.0))]

    
    def eval_vel_eq(self):
        config = self.config
        t = self.t

        v0 = np.zeros((3,1),dtype=np.float64)
        v1 = np.zeros((1,1),dtype=np.float64)

        self.vel_eq_blocks = [v0,v1,v1,v0,v0,v1,v1,v1,v1,v1,v1,v1,v1,v1]

    
    def eval_acc_eq(self):
        config = self.config
        t = self.t

        a0 = self.Pd_rbr_rocker
        a1 = self.Pd_vbs_chassis
        a2 = self.Mbar_rbr_rocker_jcr_rocker_ch[:,0:1]
        a3 = self.P_rbr_rocker
        a4 = A(a3).T
        a5 = self.Mbar_vbs_chassis_jcr_rocker_ch[:,2:3]
        a6 = B(a1,a5)
        a7 = a5.T
        a8 = self.P_vbs_chassis
        a9 = A(a8).T
        a10 = a0.T
        a11 = B(a8,a5)
        a12 = self.Mbar_rbr_rocker_jcr_rocker_ch[:,1:2]
        a13 = self.Pd_rbs_coupler
        a14 = self.Pd_rbl_rocker
        a15 = self.Mbar_rbl_rocker_jcl_rocker_ch[:,0:1]
        a16 = self.P_rbl_rocker
        a17 = A(a16).T
        a18 = self.Mbar_vbs_chassis_jcl_rocker_ch[:,2:3]
        a19 = B(a1,a18)
        a20 = a18.T
        a21 = a14.T
        a22 = B(a8,a18)
        a23 = self.Mbar_rbl_rocker_jcl_rocker_ch[:,1:2]
        a24 = self.Mbar_rbl_rocker_jcs_rc_cyl[:,0:1]
        a25 = a24.T
        a26 = self.Mbar_rbs_coupler_jcs_rc_cyl[:,2:3]
        a27 = B(a13,a26)
        a28 = a26.T
        a29 = self.P_rbs_coupler
        a30 = A(a29).T
        a31 = B(a14,a24)
        a32 = B(a16,a24).T
        a33 = B(a29,a26)
        a34 = self.Mbar_rbl_rocker_jcs_rc_cyl[:,1:2]
        a35 = a34.T
        a36 = B(a14,a34)
        a37 = B(a16,a34).T
        a38 = self.ubar_rbl_rocker_jcs_rc_cyl
        a39 = self.ubar_rbs_coupler_jcs_rc_cyl
        a40 = (multi_dot([B(a14,a38),a14]) + -1*multi_dot([B(a13,a39),a13]))
        a41 = (self.Rd_rbl_rocker + -1*self.Rd_rbs_coupler + multi_dot([B(a16,a38),a14]) + multi_dot([B(a29,a39),a13]))
        a42 = (self.R_rbl_rocker.T + -1*self.R_rbs_coupler.T + multi_dot([a38.T,a17]) + -1*multi_dot([a39.T,a30]))

        self.acc_eq_blocks = [(multi_dot([B(a0,self.ubar_rbr_rocker_jcr_rocker_ch),a0]) + -1*multi_dot([B(a1,self.ubar_vbs_chassis_jcr_rocker_ch),a1])),(multi_dot([a2.T,a4,a6,a1]) + multi_dot([a7,a9,B(a0,a2),a0]) + 2*multi_dot([a10,B(a3,a2).T,a11,a1])),(multi_dot([a12.T,a4,a6,a1]) + multi_dot([a7,a9,B(a0,a12),a0]) + 2*multi_dot([a10,B(a3,a12).T,a11,a1])),(multi_dot([B(a0,self.ubar_rbr_rocker_jcs_rc_sph),a0]) + -1*multi_dot([B(a13,self.ubar_rbs_coupler_jcs_rc_sph),a13])),(multi_dot([B(a14,self.ubar_rbl_rocker_jcl_rocker_ch),a14]) + -1*multi_dot([B(a1,self.ubar_vbs_chassis_jcl_rocker_ch),a1])),(multi_dot([a15.T,a17,a19,a1]) + multi_dot([a20,a9,B(a14,a15),a14]) + 2*multi_dot([a21,B(a16,a15).T,a22,a1])),(multi_dot([a23.T,a17,a19,a1]) + multi_dot([a20,a9,B(a14,a23),a14]) + 2*multi_dot([a21,B(a16,a23).T,a22,a1])),(multi_dot([a25,a17,a27,a13]) + multi_dot([a28,a30,a31,a14]) + 2*multi_dot([a21,a32,a33,a13])),(multi_dot([a35,a17,a27,a13]) + multi_dot([a28,a30,a36,a14]) + 2*multi_dot([a21,a37,a33,a13])),(multi_dot([a25,a17,a40]) + 2*multi_dot([a21,a32,a41]) + multi_dot([a42,a31,a14])),(multi_dot([a35,a17,a40]) + 2*multi_dot([a21,a37,a41]) + multi_dot([a42,a36,a14])),2*(multi_dot([a13.T,a13]))**(1.0/2.0),2*(multi_dot([a10,a0]))**(1.0/2.0),2*(multi_dot([a21,a14]))**(1.0/2.0)]

    
    def eval_jac_eq(self):
        config = self.config
        t = self.t

        j0 = np.eye(3,dtype=np.float64)
        j1 = self.P_rbr_rocker
        j2 = np.zeros((1,3),dtype=np.float64)
        j3 = self.Mbar_vbs_chassis_jcr_rocker_ch[:,2:3]
        j4 = j3.T
        j5 = self.P_vbs_chassis
        j6 = A(j5).T
        j7 = self.Mbar_rbr_rocker_jcr_rocker_ch[:,0:1]
        j8 = self.Mbar_rbr_rocker_jcr_rocker_ch[:,1:2]
        j9 = -1*j0
        j10 = A(j1).T
        j11 = B(j5,j3)
        j12 = self.P_rbs_coupler
        j13 = self.P_rbl_rocker
        j14 = self.Mbar_vbs_chassis_jcl_rocker_ch[:,2:3]
        j15 = j14.T
        j16 = self.Mbar_rbl_rocker_jcl_rocker_ch[:,0:1]
        j17 = self.Mbar_rbl_rocker_jcl_rocker_ch[:,1:2]
        j18 = A(j13).T
        j19 = B(j5,j14)
        j20 = self.Mbar_rbs_coupler_jcs_rc_cyl[:,2:3]
        j21 = j20.T
        j22 = A(j12).T
        j23 = self.Mbar_rbl_rocker_jcs_rc_cyl[:,0:1]
        j24 = B(j13,j23)
        j25 = self.Mbar_rbl_rocker_jcs_rc_cyl[:,1:2]
        j26 = B(j13,j25)
        j27 = j23.T
        j28 = multi_dot([j27,j18])
        j29 = self.ubar_rbl_rocker_jcs_rc_cyl
        j30 = B(j13,j29)
        j31 = self.ubar_rbs_coupler_jcs_rc_cyl
        j32 = (self.R_rbl_rocker.T + -1*self.R_rbs_coupler.T + multi_dot([j29.T,j18]) + -1*multi_dot([j31.T,j22]))
        j33 = j25.T
        j34 = multi_dot([j33,j18])
        j35 = B(j12,j20)
        j36 = B(j12,j31)

        self.jac_eq_blocks = [j0,B(j1,self.ubar_rbr_rocker_jcr_rocker_ch),j9,-1*B(j5,self.ubar_vbs_chassis_jcr_rocker_ch),j2,multi_dot([j4,j6,B(j1,j7)]),j2,multi_dot([j7.T,j10,j11]),j2,multi_dot([j4,j6,B(j1,j8)]),j2,multi_dot([j8.T,j10,j11]),j9,-1*B(j12,self.ubar_rbs_coupler_jcs_rc_sph),j0,B(j1,self.ubar_rbr_rocker_jcs_rc_sph),j0,B(j13,self.ubar_rbl_rocker_jcl_rocker_ch),j9,-1*B(j5,self.ubar_vbs_chassis_jcl_rocker_ch),j2,multi_dot([j15,j6,B(j13,j16)]),j2,multi_dot([j16.T,j18,j19]),j2,multi_dot([j15,j6,B(j13,j17)]),j2,multi_dot([j17.T,j18,j19]),j2,multi_dot([j27,j18,j35]),j2,multi_dot([j21,j22,j24]),j2,multi_dot([j33,j18,j35]),j2,multi_dot([j21,j22,j26]),-1*j28,-1*multi_dot([j27,j18,j36]),j28,(multi_dot([j27,j18,j30]) + multi_dot([j32,j24])),-1*j34,-1*multi_dot([j33,j18,j36]),j34,(multi_dot([j33,j18,j30]) + multi_dot([j32,j26])),2*j12.T,2*j1.T,2*j13.T]

    
    def eval_mass_eq(self):
        config = self.config
        t = self.t

        m0 = np.eye(3,dtype=np.float64)
        m1 = G(self.P_rbs_coupler)
        m2 = G(self.P_rbr_rocker)
        m3 = G(self.P_rbl_rocker)

        self.mass_eq_blocks = [config.m_rbs_coupler*m0,4*multi_dot([m1.T,config.Jbar_rbs_coupler,m1]),config.m_rbr_rocker*m0,4*multi_dot([m2.T,config.Jbar_rbr_rocker,m2]),config.m_rbl_rocker*m0,4*multi_dot([m3.T,config.Jbar_rbl_rocker,m3])]

    
    def eval_frc_eq(self):
        config = self.config
        t = self.t

        f0 = G(self.Pd_rbs_coupler)
        f1 = G(self.Pd_rbr_rocker)
        f2 = G(self.Pd_rbl_rocker)

        self.frc_eq_blocks = [self.F_rbs_coupler_gravity,8*multi_dot([f0.T,config.Jbar_rbs_coupler,f0,self.P_rbs_coupler]),self.F_rbr_rocker_gravity,8*multi_dot([f1.T,config.Jbar_rbr_rocker,f1,self.P_rbr_rocker]),self.F_rbl_rocker_gravity,8*multi_dot([f2.T,config.Jbar_rbl_rocker,f2,self.P_rbl_rocker])]

    
    def eval_reactions_eq(self):
        config  = self.config
        t = self.t

        Q_rbr_rocker_jcr_rocker_ch = -1*multi_dot([np.bmat([[np.eye(3,dtype=np.float64),np.zeros((1,3),dtype=np.float64).T,np.zeros((1,3),dtype=np.float64).T],[B(self.P_rbr_rocker,self.ubar_rbr_rocker_jcr_rocker_ch).T,multi_dot([B(self.P_rbr_rocker,self.Mbar_rbr_rocker_jcr_rocker_ch[:,0:1]).T,A(self.P_vbs_chassis),self.Mbar_vbs_chassis_jcr_rocker_ch[:,2:3]]),multi_dot([B(self.P_rbr_rocker,self.Mbar_rbr_rocker_jcr_rocker_ch[:,1:2]).T,A(self.P_vbs_chassis),self.Mbar_vbs_chassis_jcr_rocker_ch[:,2:3]])]]),self.L_jcr_rocker_ch])
        self.F_rbr_rocker_jcr_rocker_ch = Q_rbr_rocker_jcr_rocker_ch[0:3,0:1]
        Te_rbr_rocker_jcr_rocker_ch = Q_rbr_rocker_jcr_rocker_ch[3:7,0:1]
        self.T_rbr_rocker_jcr_rocker_ch = (-1*multi_dot([skew(multi_dot([A(self.P_rbr_rocker),self.ubar_rbr_rocker_jcr_rocker_ch])),self.F_rbr_rocker_jcr_rocker_ch]) + 0.5*multi_dot([E(self.P_rbr_rocker),Te_rbr_rocker_jcr_rocker_ch]))
        Q_rbr_rocker_jcs_rc_sph = -1*multi_dot([np.bmat([[np.eye(3,dtype=np.float64)],[B(self.P_rbr_rocker,self.ubar_rbr_rocker_jcs_rc_sph).T]]),self.L_jcs_rc_sph])
        self.F_rbr_rocker_jcs_rc_sph = Q_rbr_rocker_jcs_rc_sph[0:3,0:1]
        Te_rbr_rocker_jcs_rc_sph = Q_rbr_rocker_jcs_rc_sph[3:7,0:1]
        self.T_rbr_rocker_jcs_rc_sph = (-1*multi_dot([skew(multi_dot([A(self.P_rbr_rocker),self.ubar_rbr_rocker_jcs_rc_sph])),self.F_rbr_rocker_jcs_rc_sph]) + 0.5*multi_dot([E(self.P_rbr_rocker),Te_rbr_rocker_jcs_rc_sph]))
        Q_rbl_rocker_jcl_rocker_ch = -1*multi_dot([np.bmat([[np.eye(3,dtype=np.float64),np.zeros((1,3),dtype=np.float64).T,np.zeros((1,3),dtype=np.float64).T],[B(self.P_rbl_rocker,self.ubar_rbl_rocker_jcl_rocker_ch).T,multi_dot([B(self.P_rbl_rocker,self.Mbar_rbl_rocker_jcl_rocker_ch[:,0:1]).T,A(self.P_vbs_chassis),self.Mbar_vbs_chassis_jcl_rocker_ch[:,2:3]]),multi_dot([B(self.P_rbl_rocker,self.Mbar_rbl_rocker_jcl_rocker_ch[:,1:2]).T,A(self.P_vbs_chassis),self.Mbar_vbs_chassis_jcl_rocker_ch[:,2:3]])]]),self.L_jcl_rocker_ch])
        self.F_rbl_rocker_jcl_rocker_ch = Q_rbl_rocker_jcl_rocker_ch[0:3,0:1]
        Te_rbl_rocker_jcl_rocker_ch = Q_rbl_rocker_jcl_rocker_ch[3:7,0:1]
        self.T_rbl_rocker_jcl_rocker_ch = (-1*multi_dot([skew(multi_dot([A(self.P_rbl_rocker),self.ubar_rbl_rocker_jcl_rocker_ch])),self.F_rbl_rocker_jcl_rocker_ch]) + 0.5*multi_dot([E(self.P_rbl_rocker),Te_rbl_rocker_jcl_rocker_ch]))
        Q_rbl_rocker_jcs_rc_cyl = -1*multi_dot([np.bmat([[np.zeros((1,3),dtype=np.float64).T,np.zeros((1,3),dtype=np.float64).T,multi_dot([A(self.P_rbl_rocker),self.Mbar_rbl_rocker_jcs_rc_cyl[:,0:1]]),multi_dot([A(self.P_rbl_rocker),self.Mbar_rbl_rocker_jcs_rc_cyl[:,1:2]])],[multi_dot([B(self.P_rbl_rocker,self.Mbar_rbl_rocker_jcs_rc_cyl[:,0:1]).T,A(self.P_rbs_coupler),self.Mbar_rbs_coupler_jcs_rc_cyl[:,2:3]]),multi_dot([B(self.P_rbl_rocker,self.Mbar_rbl_rocker_jcs_rc_cyl[:,1:2]).T,A(self.P_rbs_coupler),self.Mbar_rbs_coupler_jcs_rc_cyl[:,2:3]]),(multi_dot([B(self.P_rbl_rocker,self.Mbar_rbl_rocker_jcs_rc_cyl[:,0:1]).T,(-1*self.R_rbs_coupler + multi_dot([A(self.P_rbl_rocker),self.ubar_rbl_rocker_jcs_rc_cyl]) + -1*multi_dot([A(self.P_rbs_coupler),self.ubar_rbs_coupler_jcs_rc_cyl]) + self.R_rbl_rocker)]) + multi_dot([B(self.P_rbl_rocker,self.ubar_rbl_rocker_jcs_rc_cyl).T,A(self.P_rbl_rocker),self.Mbar_rbl_rocker_jcs_rc_cyl[:,0:1]])),(multi_dot([B(self.P_rbl_rocker,self.Mbar_rbl_rocker_jcs_rc_cyl[:,1:2]).T,(-1*self.R_rbs_coupler + multi_dot([A(self.P_rbl_rocker),self.ubar_rbl_rocker_jcs_rc_cyl]) + -1*multi_dot([A(self.P_rbs_coupler),self.ubar_rbs_coupler_jcs_rc_cyl]) + self.R_rbl_rocker)]) + multi_dot([B(self.P_rbl_rocker,self.ubar_rbl_rocker_jcs_rc_cyl).T,A(self.P_rbl_rocker),self.Mbar_rbl_rocker_jcs_rc_cyl[:,1:2]]))]]),self.L_jcs_rc_cyl])
        self.F_rbl_rocker_jcs_rc_cyl = Q_rbl_rocker_jcs_rc_cyl[0:3,0:1]
        Te_rbl_rocker_jcs_rc_cyl = Q_rbl_rocker_jcs_rc_cyl[3:7,0:1]
        self.T_rbl_rocker_jcs_rc_cyl = (-1*multi_dot([skew(multi_dot([A(self.P_rbl_rocker),self.ubar_rbl_rocker_jcs_rc_cyl])),self.F_rbl_rocker_jcs_rc_cyl]) + 0.5*multi_dot([E(self.P_rbl_rocker),Te_rbl_rocker_jcs_rc_cyl]))

        self.reactions = {'F_rbr_rocker_jcr_rocker_ch':self.F_rbr_rocker_jcr_rocker_ch,'T_rbr_rocker_jcr_rocker_ch':self.T_rbr_rocker_jcr_rocker_ch,'F_rbr_rocker_jcs_rc_sph':self.F_rbr_rocker_jcs_rc_sph,'T_rbr_rocker_jcs_rc_sph':self.T_rbr_rocker_jcs_rc_sph,'F_rbl_rocker_jcl_rocker_ch':self.F_rbl_rocker_jcl_rocker_ch,'T_rbl_rocker_jcl_rocker_ch':self.T_rbl_rocker_jcl_rocker_ch,'F_rbl_rocker_jcs_rc_cyl':self.F_rbl_rocker_jcs_rc_cyl,'T_rbl_rocker_jcs_rc_cyl':self.T_rbl_rocker_jcs_rc_cyl}

