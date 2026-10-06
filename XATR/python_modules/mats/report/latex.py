import numpy as np
import matplotlib.pyplot as plt
import os.path as osp


def santitize_filename(fn):
    basename, ext = osp.splitext(fn)
    if '.' in basename:
        basename = '{'+basename+'}'
    return basename+ext


class LatexDoc:
    def __init__(self):
        self.documentclass = 'article'
        self.pkg = {}
        self.content = ''
        self.save_location = '.'

    def add_package(self, pkgname, pkgopt=None):
        self.pkg[pkgname] = pkgopt

    def add_section(self, sec):
        # print(sec)
        self.content += '\\section{{{}}}\n'.format(sec)

    def pagebreak(self):
        self.add('\\pagebreak\n')

    def add_itemize(self, items):
        self.content += '\\begin{itemize}\n'
        for it in items:
            self.content += f'\\item {it}'
        self.content += '\\end{itemize}\n'

    def add_roc_table(self, pdpc, fa, thres):
        tline = np.array([0.75, 0.80, 0.85, 0.86, 0.87, 0.88, 0.89, 0.90, 0.91,
                          0.92, 0.93, 0.94, 0.95])

        self.add('\\vskip1cm\\begin{tabular}{ccc}\n')
        self.add('\\toprule\n')
        self.add('PdPc & FA & Threshold \\\\\n')
        self.add('\\midrule\n')
        for ix in range(0, len(pdpc)):
            if not any(abs(tline - pdpc[ix]) < 1e-2):
                continue
            line = '{:> 2.0f}\\% & {: 5.2f} & {:8.6f} \\\\\n'.format(
                pdpc[ix]*100, fa[ix], thres[ix])
            self.add(line)
        self.add('\\bottomrule\n')
        self.add('\\end{tabular}\n')

    def add_comp_roc_table(self, cfgNames, rocs):
        pdpc = np.array([0.75, 0.80, 0.81, 0.82, 0.83, 0.84, 0.85, 0.86, 0.87,
                      0.88, 0.89, 0.90, 0.91, 0.92, 0.93, 0.94, 0.95])
        rocInfo = []
        for cfgName in cfgNames:
            info = {}
            info['Name'] = rocs[cfgName]['Name']
            info['Thresh'] = np.interp(pdpc, rocs[cfgName]['PdPc'],
                                       rocs[cfgName]['Threshold'], left=-1,
                                       right=-1)
            ix = info['Thresh'] > 0
            T = np.flip(info['Thresh'][ix])  # needs to be increasing
            fa = np.flip(np.interp(T, np.flip(rocs[cfgName]['Threshold']),
                                   np.flip(rocs[cfgName]['FA']),
                                   left=-1, right=-1))
            info['FA'] = -1*np.ones(info['Thresh'].shape)
            info['FA'][ix] = fa
            rocInfo.append(info)
            
        self.add((
            '\\vskip1cm\\begin{tabular}{ccccc}\n'
            '\\toprule\n'
            ' & \\multicolumn{2}{c}{Config 1} & \\multicolumn{2}{c}{Config 2}\\\\'
            '\n\\cmidrule(r){2-3} \\cmidrule(r){4-5}\n'
            'PdPc & FA & Threshold & FA & Threshold \\\\\n'
            '\\midrule\n'
        ))

        for ix in range(0, len(pdpc)):
            if rocInfo[0]['Thresh'][ix] < 0 and rocInfo[1]['Thresh'][ix] < 0:
                continue
            self.add('{:> 2.0f}\\% &'.format(pdpc[ix]*100))

            if not rocInfo[0]['Thresh'][ix] == -1:
                self.add('{: 5.2f} & {:8.6f} &'
                        .format(rocInfo[0]['FA'][ix],
                                rocInfo[0]['Thresh'][ix]))
            else:
                self.add(' -- & -- &')

            if not rocInfo[1]['Thresh'][ix] == -1:
                self.add('{: 5.2f} & {:8.6f} \\\\\n'
                        .format(rocInfo[1]['FA'][ix],
                                rocInfo[1]['Thresh'][ix]))
            else:
                self.add(' -- & -- \\\\\n')
        self.add('\\bottomrule\n')
        self.add('\\end{tabular}\n')

    def add_roc_plot(self, pdpc, fa, fn, title):
        plt.clf()
        plt.plot(fa, pdpc)
        plt.ylabel('PdPc (%)')
        plt.xlabel('False Alarms (per image)')
        plt.title(title)
        plt.ylim([0, 1])
        plt.xlim([0, fa[-1]])
        plt.grid(True)
        plt.savefig(osp.join(self.save_location, fn))
        
        fn = santitize_filename(fn)
        self.add('\\begin{center}\n')
        self.add('\\includegraphics[width=.85\\textwidth]{'+fn+'}\n')
        self.add('\\end{center}\n')

    def add_comp_roc_plot(self, roc, fn, title):
        color = ['b', 'r']
        plt.clf()
        for ix in range(len(roc)):
            plt.plot(roc[ix]['fa_img'], roc[ix]['pdpc'], color[ix])
        plt.ylabel('PdPc (%)')
        plt.xlabel('False Alarms (per image)')
        plt.title(title)
        plt.ylim([0, 1])
        plt.xlim([0, max(roc[0]['fa_img'][-1], roc[1]['fa_img'][-1])])
        plt.grid(True)
        plt.savefig(osp.join(self.save_location, fn))
        
        fn = santitize_filename(fn)
        self.add('\\begin{center}\n')
        self.add('\\includegraphics[width=.85\\textwidth]{'+fn+'}\n')
        self.add('\\end{center}\n')

    def add(self, content):
        self.content += content

    def generate(self, filename):
        fObj = open(osp.join(self.save_location, filename), 'w')
        fObj.write('\\documentclass{{{}}}\n'.format(self.documentclass))
        for pkg in self.pkg:
            if self.pkg[pkg]:
                fObj.write('\\usepackage[{}]{{{}}}\n'.format(
                    self.pkg[pkg], pkg))
            else:
                fObj.write('\\usepackage{{{}}}\n'.format(pkg))

        # TODO(Bradley): Add preamble info

        fObj.write('\\begin{document}\n')
        fObj.write(self.content)
        fObj.write('\\end{document}\n')
