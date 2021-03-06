import mne
import numpy as np
import os
import copy
import matplotlib.pyplot as plt
import statsmodels.stats.multitest as mul
#import pdfkit
from config import *
import pathlib
from plot_time_course_in_html_functions import clear_html
from plot_time_course_in_html_functions import add_str_html
from plot_time_course_in_html_functions import add_pic_topo_html
from plot_time_course_in_html_functions import get_short_legend
from plot_time_course_in_html_functions import delaete_bad_sub
from plot_time_course_in_html_functions import p_val_binary
from plot_time_course_in_html_functions import space_fdr
from compute_p_val import compute_p_val

path = os.getcwd()
list_files = os.listdir(path)

output = 'output_topo/'


topomaps = [f'{legend[0]}',
            f'{legend[1]}',
            'difference',
            'difference_with_fdr']
options = {
    'page-size':'A3',
    'orientation':'Landscape',
    'zoom':1.0,
    'no-outline':None,
    'quiet':''
}
os.makedirs(os.path.join(output, f'{legend[0]}_vs_{legend[1]}'), exist_ok=True)        

#donor data file
temp = mne.Evoked(f'{prefix}donor-ave.fif')
temp.times = np.arange(-2.000, 1.502, 0.004)
times_to_plot = np.arange(-2.0, 1.5, 0.2)

comp1_mean, comp2_mean, contr, temp1, temp2, p_val, binary, subjects1  = compute_p_val(subjects, kind, train, frequency, check_num_sens)
p_val_fdr = space_fdr(p_val)
#legend = ["Norisk", "Risk"]
rewrite = True

    ##### CONDITION1 ######
# average = 0.1 means averaging of the power data over 100 ms

temp.data = comp1_mean[204:,:]
fig = temp.plot_topomap(times = times_to_plot, average = 0.1,
                            scalings = dict(eeg=1e6, grad=1, mag=1e15), 
                            ch_type='planar1', time_unit='s', show = False, 
                            title = legend[0], colorbar = True, vmax=p_mul_topo, vmin=-p_mul_topo)

fig.savefig(os.path.join(output, legend[0] + '_vs_' + legend[1], legend[0] + '.png'), dpi = 300)
plt.close()

    ##### CONDITION2 ######
    
temp.data = comp2_mean[204:,:]
fig = temp.plot_topomap(times = times_to_plot, average = 0.1,
                            scalings = dict(eeg=1e6, grad=1, mag=1e15),
                            ch_type='planar1', time_unit='s', show = False, 
                            title = legend[1], colorbar = True, vmax=p_mul_topo, vmin=-p_mul_topo)
fig.savefig(os.path.join(output, legend[0] + '_vs_' + legend[1], legend[1] + '.png'), dpi = 300)
plt.close()
    
    ##### CONDITION2 - CONDITION1 with marks (no FDR) ######

temp.data = comp2_mean[204:,:] - comp1_mean[204:,:]
fig = temp.plot_topomap(times = times_to_plot, average = 0.1,
                            scalings = dict(eeg=1e6, grad=1, mag=1e15), 
                            ch_type='planar1', time_unit='s', show = False, 
                            title = '%s - %s'%(legend[1], legend[0]), colorbar = True, 
                            vmax=p_mul_topo_contrast, vmin=-p_mul_topo_contrast, extrapolate="local", mask = np.bool_(binary[204:,:]),
                            mask_params = dict(marker='o', markerfacecolor='w', markeredgecolor='k',
                                               linewidth=0, markersize=7, markeredgewidth=2))
fig.savefig(os.path.join(output, legend[0] + '_vs_' + legend[1],'difference.png'), dpi = 300)
plt.close()
 
    #### CONDITION2 - CONDITION1 with marks (WITH FDR) ######

binary_fdr = p_val_binary(p_val_fdr, treshold = 0.05)

temp.data = comp2_mean[204:,:] - comp1_mean[204:,:]

fig = temp.plot_topomap(times = times_to_plot, average = 0.1,
                            scalings = dict(eeg=1e6, grad=1, mag=1e15), 
                            ch_type='planar1', time_unit='s', show = False, 
                            title = '%s - %s with_fdr'%(legend[1], legend[0]), colorbar = True, 
                            vmax=p_mul_topo_fdr_contrast, vmin=-p_mul_topo_fdr_contrast, extrapolate="local", mask = np.bool_(binary_fdr[204:,:]),
                            mask_params = dict(marker='o', markerfacecolor='w', markeredgecolor='k',
                                               linewidth=0, markersize=7, markeredgewidth=2))
fig.savefig(os.path.join(output, legend[0] + '_vs_' + legend[1],'difference_with_fdr.png'), dpi = 300)
plt.close()
    

    ##### CONDITION2 - CONDITION1 cutted by thershold (WITH FDR) ######
    # ask Nikita about the following formula
temp.data = (comp2_mean[204:,:] - comp1_mean[204:,:])*binary_fdr[204:,:]

fig = temp.plot_topomap(times = times_to_plot, average = 0.1,
                            scalings = dict(eeg=1e6, grad=1, mag=1e15), 
                            ch_type='planar1', time_unit='s', show = False, 
                            title = '%s - %s (cut) with fdr'%(legend[1], legend[0]), colorbar = True, 
                            vmax=p_mul_topo_fdr_contrast, vmin=-p_mul_topo_fdr_contrast, extrapolate="local")
fig.savefig(os.path.join(output, legend[0] + '_vs_' + legend[1],'p_value_cut_with_fdr.png'), dpi = 300)
plt.close()
   

html_name = os.path.join(output, legend[0] + '_vs_' + legend[1] + '.html')
clear_html(html_name)
add_str_html(html_name, '<!DOCTYPE html>')
add_str_html(html_name, '<html>')
add_str_html(html_name, '<body>')
add_str_html(html_name, '<p style="font-size:20px;"><b> %s, average %s, %s, trained, %d subjects </b></p>' % (legend[0] + '_vs_' + legend[1], frequency, stimulus, len(subjects1)))
add_str_html(html_name, '<p style="font-size:20px;"><b> P_val < 0.05 marked (or saved from cutting) </b></p>' )
add_str_html(html_name, '<table>')
for topo in topomaps:
    add_str_html(html_name, "<tr>")
    add_pic_topo_html(html_name, os.path.join(legend[0] + '_vs_' + legend[1],topo+'.png'))
add_str_html(html_name, "</tr>")
add_str_html(html_name, '</body>')
add_str_html(html_name, '</html>')
pdf_file = html_name.replace("html", "pdf")
#pdfkit.from_file(html_name, pdf_file, configuration = config, options=options)
print('All done!')
