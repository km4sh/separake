from __future__ import division, print_function

import sys, argparse, copy, os, re
import numpy as np
import pandas as pd
import json

if 'DISPLAY' not in os.environ:
    import matplotlib as mpl
    mpl.use('Agg')

import matplotlib.pyplot as plt
import seaborn as sns

if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser(
            description='Plot the data simulated by separake_near_wall')
    parser.add_argument('-p', '--pickle', action='store_true', 
            help='Read the aggregated data table from a pickle cache')
    parser.add_argument('-s', '--show', action='store_true',
            help='Display the plots at the end of data analysis')
    parser.add_argument('dirs', type=str, nargs='+', metavar='DIR',
            help='The directory containing the simulation output files.')

    cli_args = parser.parse_args()
    plot_flag = cli_args.show
    pickle_flag = cli_args.pickle

    # metrics to take in the plot
    metrics = ['SDR', 'SIR', 'ISR', 'SAR']
    columns = ['n_echoes','gamma','seed','Speaker gender'] + metrics

    parameters = dict()
    args = []
    df = None

    for i, data_dir in enumerate(cli_args.dirs):

        print('Reading in', data_dir)

        # Read in the parameters
        with open(data_dir + '/parameters.json', 'r') as f:
            parameters_part = json.load(f)

            for key, val in parameters_part.items():
                if key in parameters and val != parameters[key]:
                    print('Warning ({}): {}={} (vs {} in {})'.format(data_dir, 
                        key, val, parameters[key], cli_args.dirs[0]))

            else:
                if i > 0:
                    print('Warning ({}): parameter {}={} was not present before'.format(data_dir, key, val))
                parameters[key] = val

        with open(data_dir + '/arguments.json', 'r') as f:
            args.append(json.load(f))

        # check if a pickle file exists for these files
        pickle_file = data_dir + '/dataframe.pickle'

        if os.path.isfile(pickle_file) and pickle_flag:
            print('Reading existing pickle file...')
            # read the pickle file
            df_part = pd.read_pickle(pickle_file)

        else:

            # reading all data files in the directory
            records = []
            for file in os.listdir(data_dir):
                if file.startswith('data_') and file.endswith('.json'):
                    with open(os.path.join(data_dir, file), 'r') as f:
                        records += json.load(f)

            # build the data table line by line
            print('  Building table')
            table = []

            src_ind_2_label = {0: 'Female', 1:'Male'}
            for record in records:
                if record['partial_length'] == 'learn':
                    record['partial_length'] = -2
                if record['partial_length'] == 'anechoic':
                    record['partial_length'] = -1
                '''
                if record['partial_length'] == -1:
                    record['partial_length'] = 'anechoic'
                '''
                for src_index in range(len(record['sdr'])):
                    table.append(
                            [ record['partial_length'], record['gamma'], record['seed'], src_ind_2_label[src_index], ]
                            + [record[m.lower()][src_index] for m in metrics]
                            )
               
            # create a pandas frame
            print('  Making PANDAS frame...')
            df_part = pd.DataFrame(table, columns=columns)
            df_part.to_pickle(pickle_file)

        if df is None:
            df = df_part
        else:
            df = pd.concat([df, df_part], ignore_index=True)

    # turns out all we need is the follow pivoted table
    perf = pd.pivot_table(df, values=metrics, index='n_echoes', columns='gamma', aggfunc=np.median)

    label_index = [x for x in perf.index if not isinstance(x, int)]
    int_index = [x for x in perf.index if isinstance(x, int)]
    index = int_index + label_index

    # Draw the figure
    print('Plotting...')

    sns.set(style='whitegrid')
    sns.plotting_context(context='paper', font_scale=1.)

    sns.set(style='whitegrid', context='paper', font_scale=1.2,
            rc={
                'figure.figsize':(3.5,3.15), 
                'lines.linewidth':1.,
                'font.family': u'Roboto',
                'font.sans-serif': [u'Roboto Thin'],
                'text.usetex': False,
                })

    # plot the results
    plt.figure()
    for i, metric in enumerate(metrics):
        ax = plt.subplot(2,2,i+1)
        perf[metric].plot(ax=ax, legend=False)
        if i == 3:
            leg = plt.legend(perf[metric].columns, 
                            title='$\gamma$',
                            frameon=True, labelspacing=0.5, 
                            framealpha=0.8, loc=6,
                            bbox_to_anchor=[1.05, 1.2])
            leg.get_frame().set_linewidth(0.0)
        plt.ylabel(metric)
        plt.xlabel('Number of echoes')

    sns.despine(offset=10, trim=False, left=True, bottom=True)

    plt.tight_layout(pad=0.5)

    plt.savefig('figures/separake_near_wall_mu.pdf',
            bbox_extra_artists=(leg,), bbox_inches='tight')

    # Now plot the final figure, that should be much nicer and go in the paper
    gamma_selection = [np.argmax(perf['SDR'].T[n]) for n in perf.index]
    print('Selected values of gamma per max SIR:')
    print([x for x in zip(perf.index, gamma_selection)])

    newdf = None
    for n, g in zip(perf.index, gamma_selection):
        I = np.logical_and(df['n_echoes'] == n, df['gamma'] == g)
        df_part = df[I][['n_echoes', 'Speaker gender'] + metrics]

        if newdf is None:
            newdf = df_part
        else:
            newdf = pd.concat([newdf, df_part], ignore_index=True)

    newdf = newdf.replace({'n_echoes': {-2:'learn', -1:'anechoic'}})

    ## Violin Plot
    sns.set(style="whitegrid", palette="pastel", color_codes=True)
    plt.figure()

    plt.subplot(2,1,1)
    g = sns.violinplot(data=newdf, x='n_echoes', y='SDR', hue='Speaker gender', x_order=index, split=True, palette={'Male':'b', 'Female':'y'})
    plt.legend(loc=0)
    plt.xlabel('')
    plt.xticks([])
    plt.yticks(range(-5,16,5))
    plt.ylim([-2.5, 14])
    sns.despine(left=True)

    plt.subplot(2,1,2)
    sns.violinplot(data=newdf, x='n_echoes', y='SIR', hue='Speaker gender', x_order=index, split=True, palette={'Male':'b', 'Female':'y'})
    plt.legend([])
    plt.xlabel('Number of echoes')
    plt.yticks(range(-5,16,5))
    plt.ylim([-2.5, 14])
    sns.despine(left=True)

    plt.tight_layout(pad=0.5)

    plt.savefig('figures/separake_near_wall_mu_violin_plot.pdf')

    ## Violin Plot
    sns.set(style="whitegrid", palette="pastel", color_codes=True)
    plt.figure()

    plt.subplot(2,1,1)
    g = sns.boxplot(data=newdf, x='n_echoes', y='SDR')
    plt.legend(loc=0)
    plt.xlabel('')
    plt.xticks([])
    plt.yticks(range(-5,16,5))
    plt.ylim([-2.5, 14])
    sns.despine(left=True)

    plt.subplot(2,1,2)
    sns.boxplot(data=newdf, x='n_echoes', y='SIR')
    plt.legend([])
    plt.xlabel('Number of echoes')
    plt.yticks(range(-5,16,5))
    plt.ylim([-2.5, 14])
    sns.despine(left=True)

    plt.tight_layout(pad=0.5)

    plt.savefig('figures/separake_near_wall_mu_box_plot.pdf')

    '''
    ## Facetgrid
    sns.set(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})
    pal = sns.cubehelix_palette(10, rot=-.25, light=.7)

    g = sns.FacetGrid(newdf, row="n_echoes", hue="n_echoes", aspect=15, size=.5, palette=pal, xlim=[-2.5, 10])
    g.map(sns.kdeplot, "SDR", clip_on=False, shade=True, alpha=1, lw=0.1, bw=.2)
    g.map(sns.kdeplot, "SDR", clip_on=False, color="w", lw=2, bw=.2)
    g.map(plt.axhline, y=0, lw=2, clip_on=False)

    # Define and use a simple function to label the plot in axes coordinates
    def label(x, color, label):
        ax = plt.gca()
        ax.text(0, .2, label, fontweight="bold", color=color, 
                ha="left", va="center", transform=ax.transAxes)

    g.map(label, "SDR")

    # Set the subplots to overlap
    g.fig.subplots_adjust(hspace=-.25)

    # Remove axes details that don't play will with overlap
    g.set_titles("")
    g.set(yticks=[])
    g.despine(bottom=True, left=True)
    '''


    if plot_flag:
        plt.show()

