import pandas as pd
import numpy as np
import os
from openeye import oechem
from rdkit.Chem import Draw
from rdkit import Chem

splits = ['wodirection_trtssplit', 'axv']
balance = True
mls = ['SVM', 'XGBoost', 'Random_Forest', 'FCNN', 'FCNN_separated', 'MPNN', 'MPNN_separated', '1NN', '5NN']

for split in splits:
    print(split)
    for ml in mls:
        print(ml)
        logdir = './Log_%s/%s/' %(split, ml)
        scoredir = './Score_%s/RepMol/' %(split)
        
        os.makedirs(scoredir, exist_ok=True)

        files = [f for f in os.listdir(logdir) if os.path.isfile(logdir+f)]
        if split == 'axv':
            files = [f for f in files if 'bothout' in f]
        
        #intialize
        if ml not in ['1NN']:
            file_ac, mmp_ac, prob_ac = None, None, -100
            col = 'prob'
        else:
            file_ac, mmp_ac, prob_ac = None, None, 100
            col = 'distance'
        
        file_nonac, mmp_nonac, prob_nonac = None, None, 100
        
        for file in files:
            #ACs
            log = pd.read_csv(logdir+file, sep='\t', index_col=0)
            log = log[log['trueY']==1]
            log = log[log['predY']==1]
            
            if log.shape[0] > 0:
                if ml not in ['1NN']:
                    prob = np.max(log[col])
                    if prob > prob_ac:
                        file_ac = file
                        idx_ac  = log.index[np.argmax(log[col])]
                        mmp_ac  = log.loc[idx_ac, 'ids']
                        prob_ac = prob
                else:
                    prob = np.min(log[col])
                    if prob < prob_ac:
                        file_ac = file
                        idx_ac  = log.index[np.argmin(log[col])]
                        mmp_ac  = log.loc[idx_ac, 'ids']
                        prob_ac = prob
                    
            #NonACs
            log = pd.read_csv(logdir+file, sep='\t', index_col=0)
            
            if 0 in log['trueY'].tolist():
                log = log[log['trueY']==0]
                log = log[log['predY']==0]
            else:
                log = log[log['trueY']==-1]
                log = log[log['predY']==-1]
            
            if log.shape[0] > 0:
                prob = np.min(log[col])
                if prob < prob_nonac:
                    file_nonac = file
                    idx_nonac  = log.index[np.argmin(log[col])]
                    mmp_nonac  = log.loc[idx_nonac, 'ids']
                    prob_nonac = prob

        data = pd.read_csv('./Dataset/Data/%s.tsv' %(file_ac.split('_')[0]), sep='\t', index_col='id')
        smi_core = data.loc[mmp_ac, 'core'].replace('R1', '*')
        smi_sub1 = data.loc[mmp_ac, 'sub1'].replace('R1', '*')
        smi_sub2 = data.loc[mmp_ac, 'sub2'].replace('R1', '*')

        mol_core = Chem.MolFromSmiles(smi_core)
        mol_sub1 = Chem.MolFromSmiles(smi_sub1)
        mol_sub2 = Chem.MolFromSmiles(smi_sub2)

        Draw.MolToFile(mol_core, scoredir+'%s_AC_core_%s_%s.svg'%(ml, file_ac.split('_')[0], mmp_ac), imageType='svg')
        Draw.MolToFile(mol_sub1, scoredir+'%s_AC_sub1_%s_%s.svg'%(ml, file_ac.split('_')[0], mmp_ac), imageType='svg')
        Draw.MolToFile(mol_sub2, scoredir+'%s_AC_sub2_%s_%s.svg'%(ml, file_ac.split('_')[0], mmp_ac), imageType='svg')
        
        data = pd.read_csv('./Dataset/Data/%s.tsv' %(file_nonac.split('_')[0]), sep='\t', index_col='id')
        smi_core = data.loc[mmp_nonac, 'core'].replace('R1', '*')
        smi_sub1 = data.loc[mmp_nonac, 'sub1'].replace('R1', '*')
        smi_sub2 = data.loc[mmp_nonac, 'sub2'].replace('R1', '*')

        mol_core = Chem.MolFromSmiles(smi_core)
        mol_sub1 = Chem.MolFromSmiles(smi_sub1)
        mol_sub2 = Chem.MolFromSmiles(smi_sub2)

        Draw.MolToFile(mol_core, scoredir+'%s_NonAC_core_%s_%s.svg'%(ml, file_nonac.split('_')[0], mmp_nonac), imageType='svg')
        Draw.MolToFile(mol_sub1, scoredir+'%s_NonAC_sub1_%s_%s.svg'%(ml, file_nonac.split('_')[0], mmp_nonac), imageType='svg')
        Draw.MolToFile(mol_sub2, scoredir+'%s_NonAC_sub2_%s_%s.svg'%(ml, file_nonac.split('_')[0], mmp_nonac), imageType='svg')