
import numpy as np
import scipy as sc
from numpy.linalg import multi_dot
from source.cython_definitions.matrix_funcs import A, B, triad as Triad
from scipy.misc import derivative
from numpy import cos, sin
from source.solvers.python_solver import solver


class inputs(object):

    def __init__(self):
        self.pt_jcr_rocker_ch = np.array([[0], [0], [0]],dtype=np.float64)
        self.ax_jcr_rocker_ch = np.array([[0], [0], [1]],dtype=np.float64)
        self.F_jcr_rocker_ch = lambda t : 0
        self.pt_jcl_rocker_ch = np.array([[0], [0], [0]],dtype=np.float64)
        self.ax_jcl_rocker_ch = np.array([[0], [0], [1]],dtype=np.float64)
        self.pt_jcs_rc_sph = np.array([[0], [0], [0]],dtype=np.float64)
        self.ax_jcs_rc_sph = np.array([[0], [0], [1]],dtype=np.float64)
        self.pt_jcs_rc_uni = np.array([[0], [0], [0]],dtype=np.float64)
        self.ax_jcs_rc_uni = np.array([[0], [0], [1]],dtype=np.float64)
        self.ax2_jcs_rc_uni = np.array([[0], [0], [1]],dtype=np.float64)
        self.R_ground = np.array([[0], [0], [0]],dtype=np.float64)
        self.P_ground = np.array([[1], [0], [0], [0]],dtype=np.float64)
        self.Rd_ground = np.array([[0], [0], [0]],dtype=np.float64)
        self.Pd_ground = np.array([[1], [0], [0], [0]],dtype=np.float64)
        self.Pg_ground = np.array([[1], [0], [0], [0]],dtype=np.float64)
        self.R_ST_rbs_coupler = np.array([[0], [0], [0]],dtype=np.float64)
        self.P_ST_rbs_coupler = np.array([[1], [0], [0], [0]],dtype=np.float64)
        self.Rd_ST_rbs_coupler = np.array([[0], [0], [0]],dtype=np.float64)
        self.Pd_ST_rbs_coupler = np.array([[1], [0], [0], [0]],dtype=np.float64)
        self.R_ST_rbr_rocker = np.array([[0], [0], [0]],dtype=np.float64)
        self.P_ST_rbr_rocker = np.array([[1], [0], [0], [0]],dtype=np.float64)
        self.Rd_ST_rbr_rocker = np.array([[0], [0], [0]],dtype=np.float64)
        self.Pd_ST_rbr_rocker = np.array([[1], [0], [0], [0]],dtype=np.float64)
        self.R_ST_rbl_rocker = np.array([[0], [0], [0]],dtype=np.float64)
        self.P_ST_rbl_rocker = np.array([[1], [0], [0], [0]],dtype=np.float64)
        self.Rd_ST_rbl_rocker = np.array([[0], [0], [0]],dtype=np.float64)
        self.Pd_ST_rbl_rocker = np.array([[1], [0], [0], [0]],dtype=np.float64)

    def eval_constants(self):

        c0 = A(self.P_ground).T
        c1 = self.pt_jcr_rocker_ch
        c2 = -1.0*multi_dot([c0,self.R_ground])
        c3 = A(self.P_ST_rbr_rocker).T
        c4 = -1.0*multi_dot([c3,self.R_ST_rbr_rocker])
        c5 = Triad(self.ax_jcr_rocker_ch,)
        c6 = self.pt_jcl_rocker_ch
        c7 = A(self.P_ST_rbl_rocker).T
        c8 = -1.0*multi_dot([c7,self.R_ST_rbl_rocker])
        c9 = Triad(self.ax_jcl_rocker_ch,)
        c10 = A(self.P_ST_rbs_coupler).T
        c11 = self.pt_jcs_rc_sph
        c12 = -1.0*multi_dot([c10,self.R_ST_rbs_coupler])
        c13 = Triad(self.ax_jcs_rc_sph,)
        c14 = self.pt_jcs_rc_uni
        c15 = Triad(self.ax_jcs_rc_uni,)

        self.ubar_ground_jcr_rocker_ch = (multi_dot([c0,c1]) + c2)
        self.ubar_ST_rbr_rocker_jcr_rocker_ch = (multi_dot([c3,c1]) + c4)
        self.Mbar_ground_jcr_rocker_ch = multi_dot([c0,c5])
        self.Mbar_ST_rbr_rocker_jcr_rocker_ch = multi_dot([c3,c5])
        self.ubar_ground_jcl_rocker_ch = (multi_dot([c0,c6]) + c2)
        self.ubar_ST_rbl_rocker_jcl_rocker_ch = (multi_dot([c7,c6]) + c8)
        self.Mbar_ground_jcl_rocker_ch = multi_dot([c0,c9])
        self.Mbar_ST_rbl_rocker_jcl_rocker_ch = multi_dot([c7,c9])
        self.ubar_ST_rbs_coupler_jcs_rc_sph = (multi_dot([c10,c11]) + c12)
        self.ubar_ST_rbr_rocker_jcs_rc_sph = (multi_dot([c3,c11]) + c4)
        self.Mbar_ST_rbs_coupler_jcs_rc_sph = multi_dot([c10,c13])
        self.Mbar_ST_rbr_rocker_jcs_rc_sph = multi_dot([c3,c13])
        self.ubar_ST_rbs_coupler_jcs_rc_uni = (multi_dot([c10,c14]) + c12)
        self.ubar_ST_rbl_rocker_jcs_rc_uni = (multi_dot([c7,c14]) + c8)
        self.Mbar_ST_rbs_coupler_jcs_rc_uni = multi_dot([c10,c15])
        self.Mbar_ST_rbl_rocker_jcs_rc_uni = multi_dot([c7,Triad(self.ax2_jcs_rc_uni,c15[0:3,1:2])])

    @property
    def q_initial(self):
        q = np.concatenate([self.R_ground,self.P_ground,self.R_ST_rbs_coupler,self.P_ST_rbs_coupler,self.R_ST_rbr_rocker,self.P_ST_rbr_rocker,self.R_ST_rbl_rocker,self.P_ST_rbl_rocker])
        return q

    @property
    def qd_initial(self):
        qd = np.concatenate([self.Rd_ground,self.Pd_ground,self.Rd_ST_rbs_coupler,self.Pd_ST_rbs_coupler,self.Rd_ST_rbr_rocker,self.Pd_ST_rbr_rocker,self.Rd_ST_rbl_rocker,self.Pd_ST_rbl_rocker])
        return qd



class numerical_assembly(object):

    def __init__(self,config):
        self.t = 0.0
        self.config = config
        self.Pg_ground = np.array([[1], [0], [0], [0]],dtype=np.float64)

        self.pos_rows = np.array([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14])
        self.pos_cols = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])

        self.vel_rows = np.array([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14])
        self.vel_cols = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])

        self.acc_rows = np.array([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14])
        self.acc_cols = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])

        self.jac_rows = np.array([0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,8,8,8,8,9,9,9,9,10,10,11,11,12,13,14])
        self.jac_cols = np.array([0,1,4,5,0,1,4,5,0,1,4,5,0,1,4,5,0,1,6,7,0,1,6,7,0,1,6,7,2,3,4,5,2,3,6,7,2,3,6,7,0,1,0,1,3,5,7])

    
    def set_q(self,q):
        self.R_ground = q[0:3,0:1]
        self.P_ground = q[3:7,0:1]
        self.R_ST_rbs_coupler = q[7:10,0:1]
        self.P_ST_rbs_coupler = q[10:14,0:1]
        self.R_ST_rbr_rocker = q[14:17,0:1]
        self.P_ST_rbr_rocker = q[17:21,0:1]
        self.R_ST_rbl_rocker = q[21:24,0:1]
        self.P_ST_rbl_rocker = q[24:28,0:1]

    
    def set_qd(self,qd):
        self.Rd_ground = qd[0:3,0:1]
        self.Pd_ground = qd[3:7,0:1]
        self.Rd_ST_rbs_coupler = qd[7:10,0:1]
        self.Pd_ST_rbs_coupler = qd[10:14,0:1]
        self.Rd_ST_rbr_rocker = qd[14:17,0:1]
        self.Pd_ST_rbr_rocker = qd[17:21,0:1]
        self.Rd_ST_rbl_rocker = qd[21:24,0:1]
        self.Pd_ST_rbl_rocker = qd[24:28,0:1]

    
    def eval_pos_eq(self):
        config = self.config
        t = self.t

        x0 = self.R_ground
        x1 = -1.0*self.R_ST_rbr_rocker
        x2 = self.P_ground
        x3 = A(x2)
        x4 = self.P_ST_rbr_rocker
        x5 = A(x4)
        x6 = x3.T
        x7 = config.Mbar_ST_rbr_rocker_jcr_rocker_ch[:,2:3]
        x8 = config.F_jcr_rocker_ch(t,)
        x9 = config.Mbar_ST_rbr_rocker_jcr_rocker_ch[:,0:1]
        x10 = -1.0*self.R_ST_rbl_rocker
        x11 = self.P_ST_rbl_rocker
        x12 = A(x11)
        x13 = config.Mbar_ST_rbl_rocker_jcl_rocker_ch[:,2:3]
        x14 = self.R_ST_rbs_coupler
        x15 = self.P_ST_rbs_coupler
        x16 = A(x15)
        x17 = -1.0*np.eye(1,dtype=np.float64)

        self.pos_eq_blocks = [(x0 + x1 + multi_dot([x3,config.ubar_ground_jcr_rocker_ch]) + -1.0*multi_dot([x5,config.ubar_ST_rbr_rocker_jcr_rocker_ch])),multi_dot([config.Mbar_ground_jcr_rocker_ch[:,0:1].T,x6,x5,x7]),multi_dot([config.Mbar_ground_jcr_rocker_ch[:,1:2].T,x6,x5,x7]),(cos(x8)*multi_dot([config.Mbar_ground_jcr_rocker_ch[:,1:2].T,x6,x5,x9]) + sin(x8)*-1.0*multi_dot([config.Mbar_ground_jcr_rocker_ch[:,0:1].T,x6,x5,x9])),(x0 + x10 + multi_dot([x3,config.ubar_ground_jcl_rocker_ch]) + -1.0*multi_dot([x12,config.ubar_ST_rbl_rocker_jcl_rocker_ch])),multi_dot([config.Mbar_ground_jcl_rocker_ch[:,0:1].T,x6,x12,x13]),multi_dot([config.Mbar_ground_jcl_rocker_ch[:,1:2].T,x6,x12,x13]),(x14 + x1 + multi_dot([x16,config.ubar_ST_rbs_coupler_jcs_rc_sph]) + -1.0*multi_dot([x5,config.ubar_ST_rbr_rocker_jcs_rc_sph])),(x14 + x10 + multi_dot([x16,config.ubar_ST_rbs_coupler_jcs_rc_uni]) + -1.0*multi_dot([x12,config.ubar_ST_rbl_rocker_jcs_rc_uni])),multi_dot([config.Mbar_ST_rbs_coupler_jcs_rc_uni[:,0:1].T,x16.T,x12,config.Mbar_ST_rbl_rocker_jcs_rc_uni[:,0:1]]),x0,(x2 + -1.0*config.Pg_ground),(x17 + (multi_dot([x15.T,x15]))**(1.0/2.0)),(x17 + (multi_dot([x4.T,x4]))**(1.0/2.0)),(x17 + (multi_dot([x11.T,x11]))**(1.0/2.0))]

    
    def eval_vel_eq(self):
        config = self.config
        t = self.t

        v0 = np.zeros((3,1),dtype=np.float64)
        v1 = np.zeros((1,1),dtype=np.float64)

        self.vel_eq_blocks = [v0,v1,v1,(v1 + -1*derivative(config.F_jcr_rocker_ch,t,0.1,1)*np.eye(1,dtype=np.float64)),v0,v1,v1,v0,v0,v1,v0,np.zeros((4,1),dtype=np.float64),v1,v1,v1]

    
    def eval_acc_eq(self):
        config = self.config
        t = self.t

        a0 = self.Pd_ground
        a1 = self.Pd_ST_rbr_rocker
        a2 = config.Mbar_ground_jcr_rocker_ch[:,0:1]
        a3 = self.P_ground
        a4 = A(a3).T
        a5 = config.Mbar_ST_rbr_rocker_jcr_rocker_ch[:,2:3]
        a6 = B(a1,a5)
        a7 = a5.T
        a8 = self.P_ST_rbr_rocker
        a9 = A(a8).T
        a10 = a0.T
        a11 = B(a8,a5)
        a12 = config.Mbar_ground_jcr_rocker_ch[:,1:2]
        a13 = config.F_jcr_rocker_ch(t,)
        a14 = config.Mbar_ST_rbr_rocker_jcr_rocker_ch[:,0:1]
        a15 = cos(a13)
        a16 = config.Mbar_ground_jcr_rocker_ch[:,1:2]
        a17 = sin(a13)
        a18 = config.Mbar_ground_jcr_rocker_ch[:,0:1]
        a19 = self.Pd_ST_rbl_rocker
        a20 = config.Mbar_ST_rbl_rocker_jcl_rocker_ch[:,2:3]
        a21 = a20.T
        a22 = self.P_ST_rbl_rocker
        a23 = A(a22).T
        a24 = config.Mbar_ground_jcl_rocker_ch[:,0:1]
        a25 = B(a19,a20)
        a26 = B(a22,a20)
        a27 = config.Mbar_ground_jcl_rocker_ch[:,1:2]
        a28 = self.Pd_ST_rbs_coupler
        a29 = config.Mbar_ST_rbl_rocker_jcs_rc_uni[:,0:1]
        a30 = config.Mbar_ST_rbs_coupler_jcs_rc_uni[:,0:1]
        a31 = self.P_ST_rbs_coupler
        a32 = a28.T

        self.acc_eq_blocks = [(multi_dot([B(a0,config.ubar_ground_jcr_rocker_ch),a0]) + -1.0*multi_dot([B(a1,config.ubar_ST_rbr_rocker_jcr_rocker_ch),a1])),(multi_dot([a2.T,a4,a6,a1]) + multi_dot([a7,a9,B(a0,a2),a0]) + 2.0*multi_dot([a10,B(a3,a2).T,a11,a1])),(multi_dot([a12.T,a4,a6,a1]) + multi_dot([a7,a9,B(a0,a12),a0]) + 2.0*multi_dot([a10,B(a3,a12).T,a11,a1])),(derivative(a13,t,0.1,2)*-1.0*np.eye(1,dtype=np.float64) + multi_dot([a14.T,a9,(a15*B(a0,a16) + a17*-1.0*B(a0,a18)),a0]) + multi_dot([(a15*multi_dot([a16.T,a4]) + a17*-1.0*multi_dot([a18.T,a4])),B(a1,a14),a1]) + 2.0*multi_dot([((a15*multi_dot([B(a3,a16),a0])).T + 'transpose'(a17,)*-1.0*multi_dot([a10,B(a3,a18).T])),B(a8,a14),a1])),(multi_dot([B(a0,config.ubar_ground_jcl_rocker_ch),a0]) + -1.0*multi_dot([B(a19,config.ubar_ST_rbl_rocker_jcl_rocker_ch),a19])),(multi_dot([a21,a23,B(a0,a24),a0]) + multi_dot([a24.T,a4,a25,a19]) + 2.0*multi_dot([a10,B(a3,a24).T,a26,a19])),(multi_dot([a21,a23,B(a0,a27),a0]) + multi_dot([a27.T,a4,a25,a19]) + 2.0*multi_dot([a10,B(a3,a27).T,a26,a19])),(multi_dot([B(a28,config.ubar_ST_rbs_coupler_jcs_rc_sph),a28]) + -1.0*multi_dot([B(a1,config.ubar_ST_rbr_rocker_jcs_rc_sph),a1])),(multi_dot([B(a28,config.ubar_ST_rbs_coupler_jcs_rc_uni),a28]) + -1.0*multi_dot([B(a19,config.ubar_ST_rbl_rocker_jcs_rc_uni),a19])),(multi_dot([a29.T,a23,B(a28,a30),a28]) + multi_dot([a30.T,A(a31).T,B(a19,a29),a19]) + 2.0*multi_dot([a32,B(a31,a30).T,B(a22,a29),a19])),np.zeros((3,1),dtype=np.float64),np.zeros((4,1),dtype=np.float64),2.0*(multi_dot([a32,a28]))**(1.0/2.0),2.0*(multi_dot([a1.T,a1]))**(1.0/2.0),2.0*(multi_dot([a19.T,a19]))**(1.0/2.0)]

    
    def eval_jac_eq(self):
        config = self.config
        t = self.t

        j0 = np.eye(3,dtype=np.float64)
        j1 = self.P_ground
        j2 = np.zeros((1,3),dtype=np.float64)
        j3 = config.Mbar_ST_rbr_rocker_jcr_rocker_ch[:,2:3]
        j4 = j3.T
        j5 = self.P_ST_rbr_rocker
        j6 = A(j5).T
        j7 = config.Mbar_ground_jcr_rocker_ch[:,0:1]
        j8 = config.Mbar_ground_jcr_rocker_ch[:,1:2]
        j9 = -1.0*j0
        j10 = A(j1).T
        j11 = B(j5,j3)
        j12 = config.Mbar_ST_rbr_rocker_jcr_rocker_ch[:,0:1]
        j13 = config.F_jcr_rocker_ch(t,)
        j14 = cos(j13)
        j15 = config.Mbar_ground_jcr_rocker_ch[:,1:2]
        j16 = config.Mbar_ground_jcr_rocker_ch[:,0:1]
        j17 = config.Mbar_ST_rbl_rocker_jcl_rocker_ch[:,2:3]
        j18 = j17.T
        j19 = self.P_ST_rbl_rocker
        j20 = A(j19).T
        j21 = config.Mbar_ground_jcl_rocker_ch[:,0:1]
        j22 = config.Mbar_ground_jcl_rocker_ch[:,1:2]
        j23 = B(j19,j17)
        j24 = self.P_ST_rbs_coupler
        j25 = config.Mbar_ST_rbl_rocker_jcs_rc_uni[:,0:1]
        j26 = config.Mbar_ST_rbs_coupler_jcs_rc_uni[:,0:1]

        self.jac_eq_blocks = [j0,B(j1,config.ubar_ground_jcr_rocker_ch),j9,-1.0*B(j5,config.ubar_ST_rbr_rocker_jcr_rocker_ch),j2,multi_dot([j4,j6,B(j1,j7)]),j2,multi_dot([j7.T,j10,j11]),j2,multi_dot([j4,j6,B(j1,j8)]),j2,multi_dot([j8.T,j10,j11]),j2,multi_dot([j12.T,j6,(j14*B(j1,j15) + sin(j13)*-1.0*B(j1,j16))]),j2,multi_dot([(j14*multi_dot([j15.T,j10]) + sin(j13)*-1.0*multi_dot([j16.T,j10])),B(j5,j12)]),j0,B(j1,config.ubar_ground_jcl_rocker_ch),j9,-1.0*B(j19,config.ubar_ST_rbl_rocker_jcl_rocker_ch),j2,multi_dot([j18,j20,B(j1,j21)]),j2,multi_dot([j21.T,j10,j23]),j2,multi_dot([j18,j20,B(j1,j22)]),j2,multi_dot([j22.T,j10,j23]),j0,B(j24,config.ubar_ST_rbs_coupler_jcs_rc_sph),j9,-1.0*B(j5,config.ubar_ST_rbr_rocker_jcs_rc_sph),j0,B(j24,config.ubar_ST_rbs_coupler_jcs_rc_uni),j9,-1.0*B(j19,config.ubar_ST_rbl_rocker_jcs_rc_uni),j2,multi_dot([j25.T,j20,B(j24,j26)]),j2,multi_dot([j26.T,A(j24).T,B(j19,j25)]),j0,np.zeros((3,4),dtype=np.float64),np.zeros((4,3),dtype=np.float64),np.eye(4,dtype=np.float64),2.0*j24.T,2.0*j5.T,2.0*j19.T]
  