#%%
import argparse
import glob
import os
import random
import sys
from pathlib import Path

import torch
from imageio import imread
from msd_pytorch import MSDRegressionModel
from torch import nn
from torch.utils.data import DataLoader

import src.models as models
import src.test_model as test
import src.transfer_model as transfer
import src.utils as utils
from src.image_dataset import MultiOrbitDataset
from src.utils import ValSampler, _nat_sort


#%%
# Sets arguments here to be used as a notebook
GPU_ID = 2
if 'CUDA_VISIBLE_DEVICES' not in os.environ.keys():
    torch.cuda.set_device(GPU_ID)

print(f"Running on GPU: {torch.cuda.current_device()}, {torch.cuda.get_device_name(torch.cuda.current_device())}", 
        flush=True)


#%%
def SVCCA():
    pass

SVCCA()

#%%
def plot_weights_evolution():
    model_params = {'c_in': 1, 'c_out': 1, 'depth': 30, 'width': 1,
                        'dilations': [1,2,4,8,16], 'loss': 'L2'}
    model = MSDRegressionModel(**model_params)

    transfer.plot_weights_dist(model.msd, list(map(lambda f: torch.load(f), sorted(Path('model_weights/MSD_d30_fW_1127195514/').glob('model_*.h5'), key=_nat_sort))),
                      title='norm fW', filename='weight_norm_scratch_fW.png')
    # transfer.plot_weights_dist(model.msd, list(map(lambda f: torch.load(f), sorted(Path('model_weights/MSD_d30_fW_over_1211191235/').glob('model_*.h5'), key=_nat_sort))),
    #                   title='std nP1', filename='weight_std_transfer_nP1.png')

plot_weights_evolution()

#%%
def compare_models():
    model_params = {'c_in': 1, 'c_out': 1, 'depth': 30, 'width': 1,
                    'dilations': [1, 2, 4, 8, 16], 'loss': 'L2'}

    folders = sorted(list(Path('model_weights').glob('MSD_d30_transfer_nP0[0-9]_[0-9]*/')), key=_nat_sort)
    print(folders)
    models = [MSDRegressionModel(**model_params) for _ in range(len(folders))]

    target_ims, input_ims = utils.load_phantom_ds()
    te_ds = MultiOrbitDataset([input_ims[-1]], [target_ims[-1]], data_augmentation=False)
    norm_dl = DataLoader(te_ds, batch_size=50, sampler=ValSampler(len(te_ds), 200))

    state_dicts = [torch.load(sorted(folder.glob('model*.h5'), key=_nat_sort)[-1]) for folder in folders]
    [model.msd.load_state_dict(state_dict) for model, state_dict in zip(models, state_dicts)]
    [model.set_normalization(norm_dl) for model in models]

    te_dl = DataLoader(te_ds, batch_size=1, sampler=ValSampler(len(te_ds), 200))    
    test.compare_models(models, te_dl, names=[f'{i+1} Phantom(s)' for i in range(len(folders))], title='Training with increasingly more phantoms    ')

compare_models()

#%%
def plot_losses():
    for _ in utils.split_data_CV(list(range(4)), list(range(4)), frac=(0, 3/4)): pass
    
    phantoms_LOOCV = [f'Phantom{i}' for i in [7, 3, 1, 6]]    
    phantoms_LOICV = [f'Phantom{i}' for i in [6, 7, 3, 0]]

    folders = sorted(list(Path('model_weights').glob('MSD_d30_P_scratch_nP0[0-9]_[0-9]*/')), key=_nat_sort)
    print(folders)
    # folders = [folder for _, folder in sorted(zip(phantoms_LOICV, folders))]

    test.compare_loss(*folders, names=[f'{i+1} Phantom(s)' for i in range(3)])

plot_losses()

#%%
def test_model():

    model_params = {'c_in': 1, 'c_out': 1, 'depth': 30, 'width': 1,
                        'dilations': [1,2,4,8,16], 'loss': 'L2'}

    #===== Walnuts =====#
    # model1, model2 = MSDRegressionModel(**model_params), MSDRegressionModel(**model_params)

    # target_ims, input_ims = utils.load_walnut_ds()
    # test_set, _, _ = utils.split_data(input_ims, target_ims)

    # te_ds = MultiOrbitDataset(*test_set, data_augmentation=False)
    # norm_dl = DataLoader(te_ds, batch_size=50, sampler=ValSampler(len(te_ds), 200))

    # state_dict1 = torch.load(sorted(glob.glob('model_weights/MSD_d30_fW_1127195514/model*.h5'), key=_nat_sort)[-1])
    # state_dict2 = torch.load(sorted(glob.glob('model_weights/MSD_d80_fW*/model*.h5'), key=_nat_sort)[-1])

    # model1.msd.load_state_dict(state_dict1)
    # model2.msd.load_state_dict(state_dict2)

    # model1.set_normalization(norm_dl)
    # model2.set_normalization(norm_dl)

    # te_dl = DataLoader(te_ds, batch_size=1, sampler=ValSampler(len(te_ds), 200))    
    # test.compare_models((model1, model2), te_dl, names=['Scratch', 'Scratch expLR'], title='Walnut models, on Phantoms')

    # metrics1 = test.test(model1, te_dl)
    # metrics2 = test.test(model2, te_dl)

    # print("Model1:\n\tMSE={0:.3e}+-{1:.3e}\n\tSSIM={2:.4f}+-{3:.3e}\n\tDSC={4:.4f}+-{5:.3e}".format(
    #     metrics1[0][0], metrics1[1][0], metrics1[0][1], metrics1[1][1], metrics1[0][2], metrics1[1][2]))

    # print("Model2:\n\tMSE={0:.3e}+-{1:.3e}\n\tSSIM={2:.4f}+-{3:.3e}\n\tDSC={4:.4f}+-{5:.3e}".format(
    #     metrics2[0][0], metrics2[1][0], metrics2[0][1], metrics2[1][1], metrics2[0][2], metrics2[1][2]))

     #===== Phantoms =====#
    

    # metrics1 = test.test(model1, te_dl)
    # metrics2 = test.test(model2, te_dl)
    # metrics3 = test.test(model3, te_dl)

    # print("Model1:\n\tMSE={0:.3e}+-{1:.3e}\n\tSSIM={2:.4f}+-{3:.3e}\n\tDSC={4:.4f}+-{5:.3e}".format(
    #     metrics1[0][0], metrics1[1][0], metrics1[0][1], metrics1[1][1], metrics1[0][2], metrics1[1][2]))

    # print("Model2:\n\tMSE={0:.3e}+-{1:.3e}\n\tSSIM={2:.4f}+-{3:.3e}\n\tDSC={4:.4f}+-{5:.3e}".format(
    #     metrics2[0][0], metrics2[1][0], metrics2[0][1], metrics2[1][1], metrics2[0][2], metrics2[1][2]))
    # print("Model3:\n\tMSE={0:.3e}+-{1:.3e}\n\tSSIM={2:.4f}+-{3:.3e}\n\tDSC={4:.4f}+-{5:.3e}".format(
    #     metrics3[0][0], metrics3[1][0], metrics3[0][1], metrics3[1][1], metrics3[0][2], metrics3[1][2]))
    

    # model = MSDRegressionModel(**model_params)
    # state_dicts = sorted(glob.glob('model_weights/MSD_d30_fW_over_1211191235/model*.h5'), key=_nat_sort)
    # state_dicts = [state_dicts[-1]] +sorted(glob.glob('model_weights/MSD_d30_APhantoms_transfer_1121150812/model*.h5'), key=_nat_sort)
    # model.msd.load_state_dict(torch.load(state_dicts[-1]))

    # target_ims, input_ims = utils.load_walnut_ds()
    # test_set, val_set, train_set = utils.split_data(input_ims, target_ims)        

    # te_dl = DataLoader(te_ds, batch_size=32, sampler=ValSampler(len(te_ds), 64))
    # test.noise_robustness(model, te_dl, noise='gaussian', title="Gaussian noise")

    # te_ds = MultiOrbitDataset(*test_set, data_augmentation=False)
    # model.set_normalization(DataLoader(te_ds, batch_size=50, sampler=ValSampler(len(te_ds), 200)))
    # test.plot_metrics_evolution(model, state_dicts, te_ds, title='Walnut model on te_Walnuts', 
    #                             filename='outputs/fW_metrics_Wte.png')

    # val_ds = MultiOrbitDataset(*val_set, data_augmentation=False)
    # model.set_normalization(DataLoader(val_ds, batch_size=50, sampler=ValSampler(len(val_ds), 200)))     
    # test.plot_metrics_evolution(model, state_dicts, val_ds, title='Walnut model on val_Walnuts', 
    #                             filename='outputs/fW_metrics_Wval.png')

    # tr_ds = MultiOrbitDataset(*train_set, data_augmentation=False)
    # model.set_normalization(DataLoader(tr_ds, batch_size=50, sampler=ValSampler(len(tr_ds), 200)))                  
    # test.plot_metrics_evolution(model, state_dicts, tr_ds, title='Walnut model on tr_Walnuts', 
    #                             filename='outputs/fW_metrics_Wtr.png')
    
    # target_ims, input_ims = utils.load_phantom_ds()
    # ph_ds = MultiOrbitDataset(input_ims, target_ims, data_augmentation=False)
    # model.set_normalization(DataLoader(ph_ds, batch_size=50, sampler=ValSampler(len(ph_ds), 200)))
    # test.plot_metrics_evolution(model, state_dicts, ph_ds, title='Walnut model on Phantoms', 
    #                             filename='outputs/fW_metrics_P.png')
    

    # model = MSDRegressionModel(**model_params)
    # target_ims, input_ims = utils.load_phantom_ds()

    # te_ds = MultiOrbitDataset([target_ims[3]], [input_ims[3]], data_augmentation=False)
    # norm_dl = DataLoader(te_ds, batch_size=50, sampler=ValSampler(len(te_ds), 200))

    # model.set_normalization(norm_dl)
    # state_dicts = sorted(Path('model_weights/MSD_d30_P_scratch_CV0_1214101104/').glob('model*.h5'))
    # test.plot_metrics_evolution(model, state_dicts, te_ds, filename='outputs/CV0')

#%%
def main():
    # Sets available GPU if not already set in env vars
    if 'CUDA_VISIBLE_DEVICES' not in os.environ.keys():
        torch.cuda.set_device(globals().get('GPU_ID', -1))

    print(f"Running on GPU: {torch.cuda.current_device()}, {torch.cuda.get_device_name(torch.cuda.current_device())}", 
          flush=True)

    test_model()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--gpu', type=int, nargs='?', default=2,
                        help='GPU to run astra sims on')
    args = parser.parse_args()

    GPU_ID = args.gpu

    main()

#ää