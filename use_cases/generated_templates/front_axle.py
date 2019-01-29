
import numpy as np

import dwb
import steer
import test_rig

SU1_config = dwb.configuration()
SU1 = dwb.topology(SU1_config,'SU1')

ST_config = steer.configuration()
ST = steer.topology(ST_config,'ST')

TR_config = test_rig.configuration()
TR = test_rig.topology(TR_config,'TR')



class numerical_assembly(object):

    def __init__(self):
        self.Pg_ground  = np.array([[1],[0],[0],[0]],dtype=np.float64)
        self.subsystems = [SU1,ST,TR]

        self.interface_map = {'SU1.vbl_steer': 'ST.rbl_rocker', 'SU1.vbr_steer': 'ST.rbr_rocker', 'SU1.vbs_ground': 'ground', 'SU1.vbs_chassis': 'ground', 'ST.vbs_chassis': 'ground', 'ST.vbs_ground': 'ground', 'TR.vbr_hub': 'SU1.rbr_hub', 'TR.vbr_upright': 'SU1.rbr_upright', 'TR.vbl_hub': 'SU1.rbl_hub', 'TR.vbl_upright': 'SU1.rbl_upright', 'TR.vbs_ground': 'ground'}
        self.indicies_map  = {'ground': 0, 'SU1.rbr_uca': 1, 'SU1.rbl_uca': 2, 'SU1.rbr_lca': 3, 'SU1.rbl_lca': 4, 'SU1.rbr_upright': 5, 'SU1.rbl_upright': 6, 'SU1.rbr_upper_strut': 7, 'SU1.rbl_upper_strut': 8, 'SU1.rbr_lower_strut': 9, 'SU1.rbl_lower_strut': 10, 'SU1.rbr_tie_rod': 11, 'SU1.rbl_tie_rod': 12, 'SU1.rbr_hub': 13, 'SU1.rbl_hub': 14, 'ST.rbs_coupler': 15, 'ST.rbr_rocker': 16, 'ST.rbl_rocker': 17}

    def set_time(self,t):
        for sub in self.subsystems:
            sub.t = t

    def assemble_system(self):
        offset = 0
        for sub in self.subsystems:
            sub.assemble_template(self.indicies_map,self.interface_map,offset)
            offset += sub.nrows
        self.rows = np.concatenate([s.rows for s in self.subsystems])
        self.jac_rows = np.concatenate([s.jac_rows for s in self.subsystems])
        self.jac_cols = np.concatenate([s.jac_cols for s in self.subsystems])

    
    def eval_constants(self):
        SU1.config.R_vbl_steer = ST.config.R_rbl_rocker
        SU1.config.P_vbl_steer = ST.config.P_rbl_rocker
        SU1.config.R_vbr_steer = ST.config.R_rbr_rocker
        SU1.config.P_vbr_steer = ST.config.P_rbr_rocker
        SU1.config.R_vbs_ground = self.R_ground
        SU1.config.P_vbs_ground = self.P_ground
        SU1.config.R_vbs_chassis = self.R_ground
        SU1.config.P_vbs_chassis = self.P_ground
        ST.config.R_vbs_chassis = self.R_ground
        ST.config.P_vbs_chassis = self.P_ground
        ST.config.R_vbs_ground = self.R_ground
        ST.config.P_vbs_ground = self.P_ground
        TR.config.R_vbr_hub = SU1.config.R_rbr_hub
        TR.config.P_vbr_hub = SU1.config.P_rbr_hub
        TR.config.R_vbr_upright = SU1.config.R_rbr_upright
        TR.config.P_vbr_upright = SU1.config.P_rbr_upright
        TR.config.R_vbl_hub = SU1.config.R_rbl_hub
        TR.config.P_vbl_hub = SU1.config.P_rbl_hub
        TR.config.R_vbl_upright = SU1.config.R_rbl_upright
        TR.config.P_vbl_upright = SU1.config.P_rbl_upright
        TR.config.R_vbs_ground = self.R_ground
        TR.config.P_vbs_ground = self.P_ground

        for sub in self.subsystems:
            sub.config.eval_constants()

    
    def set_gen_coordinates(self,q):
        self.R_ground = q[0:3,0:1]
        self.P_ground = q[3:7,0:1]
        offset = 7
        for sub in self.subsystems:
            qs = q[offset:sub.n]
            sub.set_gen_coordinates(qs)
            offset += sub.n

        SU1.R_vbl_steer = ST.R_rbl_rocker
        SU1.P_vbl_steer = ST.P_rbl_rocker
        SU1.R_vbr_steer = ST.R_rbr_rocker
        SU1.P_vbr_steer = ST.P_rbr_rocker
        SU1.R_vbs_ground = self.R_ground
        SU1.P_vbs_ground = self.P_ground
        SU1.R_vbs_chassis = self.R_ground
        SU1.P_vbs_chassis = self.P_ground
        ST.R_vbs_chassis = self.R_ground
        ST.P_vbs_chassis = self.P_ground
        ST.R_vbs_ground = self.R_ground
        ST.P_vbs_ground = self.P_ground
        TR.R_vbr_hub = SU1.R_rbr_hub
        TR.P_vbr_hub = SU1.P_rbr_hub
        TR.R_vbr_upright = SU1.R_rbr_upright
        TR.P_vbr_upright = SU1.P_rbr_upright
        TR.R_vbl_hub = SU1.R_rbl_hub
        TR.P_vbl_hub = SU1.P_rbl_hub
        TR.R_vbl_upright = SU1.R_rbl_upright
        TR.P_vbl_upright = SU1.P_rbl_upright
        TR.R_vbs_ground = self.R_ground
        TR.P_vbs_ground = self.P_ground

    
    def set_gen_velocities(self,qd):
        self.Rd_ground = qd[0:3,0:1]
        self.Pd_ground = qd[3:7,0:1]
        offset = 7
        for sub in self.subsystems:
            qs = qd[offset:sub.n]
            sub.set_gen_velocities(qs)
            offset += sub.n

        SU1.Rd_vbl_steer = ST.Rd_rbl_rocker
        SU1.Pd_vbl_steer = ST.Pd_rbl_rocker
        SU1.Rd_vbr_steer = ST.Rd_rbr_rocker
        SU1.Pd_vbr_steer = ST.Pd_rbr_rocker
        SU1.Rd_vbs_ground = self.Rd_ground
        SU1.Pd_vbs_ground = self.Pd_ground
        SU1.Rd_vbs_chassis = self.Rd_ground
        SU1.Pd_vbs_chassis = self.Pd_ground
        ST.Rd_vbs_chassis = self.Rd_ground
        ST.Pd_vbs_chassis = self.Pd_ground
        ST.Rd_vbs_ground = self.Rd_ground
        ST.Pd_vbs_ground = self.Pd_ground
        TR.Rd_vbr_hub = SU1.Rd_rbr_hub
        TR.Pd_vbr_hub = SU1.Pd_rbr_hub
        TR.Rd_vbr_upright = SU1.Rd_rbr_upright
        TR.Pd_vbr_upright = SU1.Pd_rbr_upright
        TR.Rd_vbl_hub = SU1.Rd_rbl_hub
        TR.Pd_vbl_hub = SU1.Pd_rbl_hub
        TR.Rd_vbl_upright = SU1.Rd_rbl_upright
        TR.Pd_vbl_upright = SU1.Pd_rbl_upright
        TR.Rd_vbs_ground = self.Rd_ground
        TR.Pd_vbs_ground = self.Pd_ground

    
    def eval_pos_eq(self):

        self.pos_eq_blocks = [self.R_ground,(-1.0*'Pg_ground' + self.P_ground)]

        for sub in self.subsystems:
            sub.eval_pos_eq()
        self.pos_blocks = sum([s.pos_blocks for s in self.subsystems],[])

    
    def eval_vel_eq(self):

        self.vel_eq_blocks = [np.zeros((3,1),dtype=np.float64),np.zeros((4,1),dtype=np.float64)]

        for sub in self.subsystems:
            sub.eval_vel_eq()
        self.vel_blocks = sum([s.vel_blocks for s in self.subsystems],[])

    
    def eval_acc_eq(self):

        self.acc_eq_blocks = [np.zeros((3,1),dtype=np.float64),np.zeros((4,1),dtype=np.float64)]

        for sub in self.subsystems:
            sub.eval_acc_eq()
        self.acc_blocks = sum([s.acc_blocks for s in self.subsystems],[])

    
    def eval_jac_eq(self):

        self.jac_eq_blocks = [np.eye(3,dtype=np.float64),np.zeros((3,4),dtype=np.float64),np.zeros((4,3),dtype=np.float64),np.eye(4,dtype=np.float64)]

        for sub in self.subsystems:
            sub.eval_jac_eq()
        self.jac_blocks = sum([s.jac_blocks for s in self.subsystems],[])
  