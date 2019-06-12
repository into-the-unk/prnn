import torch
import numpy as np
import os, sys, optparse

import config, utils
from config import device, model as model_config
from model import PerformanceRNN
from sequence import EventSeq, Control, ControlSeq

# pylint: disable=E1101,E1102

# output = [130, 135, 212, 194, 210, 134, 208, 132, 135, 40, 213, 219, 133, 211, 121, 191, 128, 126, 213, 236, 116, 36, 61, 126, 212, 41, 209, 228, 231, 60, 23, 228, 216, 199, 42, 189, 155, 124, 218, 208, 197, 212, 131, 211, 208, 230, 123, 212, 226, 118, 106, 216, 188, 116, 30, 127, 218, 58, 112, 195, 235, 123, 128, 210, 185, 42, 135, 192, 199, 57, 210, 223, 238, 223, 214, 45, 188, 189, 128, 38, 137, 221, 137, 133, 213, 182, 228, 209, 130, 224, 29, 226, 137, 192, 55, 211, 187, 161, 185, 217, 123, 16, 208, 60, 216, 37, 37, 180, 134, 123, 220, 47, 222, 184, 198, 37, 40, 211, 119, 188, 210, 224, 132, 212, 131, 200, 18, 193, 221, 184, 226, 203, 126, 30, 111, 208, 231, 43, 198, 37, 198, 18, 180, 137, 201, 134, 213, 128, 181, 213, 228, 135, 41, 25, 21, 193, 133, 135, 43, 111, 187, 211, 111, 118, 200, 141, 147, 217, 143, 215, 186, 159, 116, 197, 198, 197, 147, 196, 224, 33, 57, 192, 213, 200, 123, 139, 148, 133, 104, 142, 193, 6, 131, 139, 137, 55, 211, 184, 193, 133, 213, 135, 222, 131, 201, 54, 187, 211, 221, 132, 116, 215, 212, 198, 31, 219, 37, 213, 185, 196, 194, 232, 135, 192, 221, 214, 214, 208, 221, 143, 185, 127, 123, 216, 198, 46, 47, 197, 119, 131, 198, 214, 229, 215, 236, 213, 228, 133, 140, 111, 42, 35, 226, 214, 138, 38, 198, 28, 131, 23, 128, 106, 116, 197, 122, 181, 131, 215, 29, 191, 126, 215, 144, 197, 189, 212, 128, 194, 227, 142, 189, 219, 193, 225, 143, 49, 121, 185, 220, 177, 61, 219, 188, 185, 184, 123, 30, 208, 212, 227, 134, 43, 209, 27, 221, 143, 220, 221, 193, 215, 54, 43, 54, 193, 191, 64, 209, 223, 113, 209, 209, 141, 115, 216, 149, 218, 228, 223, 21, 119, 186, 116, 212, 235, 192, 230, 189, 208, 219, 220, 42, 215, 223, 225, 142, 43, 211, 135, 220, 138, 35, 231, 196, 215, 45, 119, 224, 38, 213, 54, 61, 235, 122, 225, 35, 181, 123, 235, 192, 133, 218, 221, 216, 198, 197, 123, 32, 52, 199, 147, 211, 194, 226, 218, 59, 59, 222, 114, 198, 224, 212, 201, 221, 184, 42, 217, 52, 123, 189, 218, 225, 197, 230, 198, 56, 214, 143, 37, 198, 229, 197, 104, 218, 214, 129, 214, 200, 229, 197, 140, 188, 139, 131, 184, 211, 211, 199, 187, 185, 188, 135, 212, 43, 183, 179, 239, 53, 210, 139, 227, 179, 218, 136, 28, 208, 135, 225, 57, 54, 128, 214, 178, 199, 227, 44, 188, 191, 179, 116, 225, 215, 39, 224, 181, 143, 51, 134, 200, 140, 172, 40, 184, 202, 51, 123, 118, 226, 40, 220, 194, 20, 143, 227, 226, 52, 128, 225, 220, 219, 199, 130, 211, 215, 115, 190, 189, 223, 193, 199, 118, 184, 128, 222, 200, 198, 198, 222, 210, 196, 214, 194, 135, 221, 193, 192, 196, 217, 220, 232, 128, 218, 45, 180, 194, 196, 116, 181, 220, 208, 124, 127, 59, 185, 159, 136, 197, 194, 213, 118, 199, 43, 33, 197, 212, 218, 147, 52, 200, 119, 52, 139, 219, 187, 47, 225, 121, 208, 122, 232, 42, 198, 203, 43, 127, 123, 135, 211, 193, 184, 227, 46, 216, 124, 47, 195, 134, 56, 145, 217, 188, 239, 184, 138, 219, 219, 215, 121, 185, 220, 213, 40, 140, 198, 214, 119, 184, 106, 239, 178, 194, 184, 106, 198, 208, 219, 231, 38, 225, 18, 187, 214, 142, 40, 47, 201, 141, 194, 134, 208, 189, 121, 190, 222, 47, 53, 198, 195, 43, 35, 179, 214, 200, 140, 184, 197, 218, 61, 142, 184, 186, 52, 133, 222, 45, 208, 190, 133, 179, 234, 142, 221, 131, 57, 227, 35, 132, 192, 200, 189, 124, 145, 183, 218, 143, 196, 106, 211, 194, 117, 40, 237, 209, 123, 46, 35, 118, 188, 128, 111, 46, 132, 212, 30, 225, 213, 47, 198, 208, 157, 227, 194, 42, 230, 31, 49, 31, 186, 225, 211, 55, 235, 131, 55, 47, 30, 220, 215, 55, 34, 188, 62, 189, 184, 194, 45, 210, 218, 24, 185, 223, 128, 197, 194, 210, 58, 214, 54, 53, 189, 209, 194, 216, 113, 197, 47, 226, 132, 35, 186, 225, 52, 196, 18, 104, 123, 193, 221, 220, 218, 186, 42, 218, 133, 215, 127, 221, 149, 28, 135, 45, 197, 43, 190, 35, 200, 227, 219, 40, 238, 209, 28, 23, 180, 227, 219, 195, 228, 212, 118, 229, 214, 128, 212, 47, 51, 33, 189, 190, 211, 216, 38, 208, 176, 25, 230, 216, 208, 209, 193, 128, 55, 215, 194, 43, 35, 197, 28, 220, 209, 52, 144, 196, 219, 56, 199, 228, 127, 131, 31, 198, 35, 198, 147, 225, 43, 208, 119, 233, 26, 208, 23, 223, 143, 176, 214, 214, 216, 189, 139, 192, 212, 121, 186, 131, 127, 226, 218, 49, 196, 62, 214, 197, 198, 135, 218, 213, 186, 227, 55, 28, 224, 43, 196, 23, 24, 189, 186, 125, 132, 204, 49, 211, 188, 131, 182, 239, 190, 140, 73, 225, 142, 216, 212, 117, 197, 127, 217, 184, 216, 214, 34, 137, 183, 138, 220, 224, 25, 38, 59, 201, 186, 196, 22, 123, 227, 185, 195, 205, 52, 196, 223, 33, 229, 33, 222, 116, 199, 183, 198, 54, 150, 194, 45, 223, 217, 234, 47, 198, 43, 214, 131, 210, 21, 42, 127, 47, 215, 193, 45, 184, 40, 57, 38, 227, 133, 219, 195, 123, 196, 219, 191, 208, 111, 39, 211, 118, 28, 26, 52, 140, 194, 36, 191, 116, 132, 211, 44, 210, 217, 218, 190, 216, 35, 56, 182, 136, 215, 197, 42, 208, 211, 211, 186, 132, 221, 52, 210, 219, 198, 199, 194, 148, 193, 231, 181, 214, 42, 40, 131]
output = [209, 18, 221, 216, 233, 113, 179, 135, 179, 33, 227, 126, 34, 210, 195, 132, 182, 124, 135, 184, 113, 216, 52, 131, 134, 220, 131, 185, 205, 192, 215, 50, 116, 121, 221, 142, 226, 126, 220, 128, 50, 140, 141, 194, 29, 231, 195, 45, 235, 155, 218, 196, 225, 189, 218, 217, 218, 32, 228, 212, 35, 199, 216, 182, 208, 114, 215, 179, 224, 210, 186, 199, 195, 213, 217, 195, 208, 219, 144, 31, 226, 43, 188, 200, 188, 227, 218, 131, 211, 49, 225, 17, 25, 52, 227, 192, 196, 219, 30, 134, 147, 147, 45, 219, 111, 45, 187, 61, 223, 239, 180, 185, 195, 142, 28, 197, 221, 27, 119, 208, 222, 24, 214, 222, 139, 109, 214, 147, 35, 46, 47, 219, 220, 230, 135, 33, 187, 216, 203, 220, 200, 191, 208, 53, 213, 23, 192, 221, 230, 193, 119, 211, 147, 217, 218, 37, 198, 193, 143, 118, 56, 200, 43, 193, 222, 43, 185, 128, 18, 119, 47, 228, 26, 159, 217, 192, 215, 176, 139, 214, 211, 131, 209, 122, 224, 129, 138, 220, 201, 141, 128, 187, 231, 24, 125, 40, 144, 34, 123, 213, 189, 33, 142, 54, 47, 45, 225, 191, 111, 209, 54, 211, 111, 213, 212, 218, 215, 226, 184, 221, 237, 123, 188, 210, 199, 200, 47, 228, 46, 191, 218, 40, 26, 210, 94, 198, 216, 180, 193, 37, 210, 210, 220, 132, 45, 198, 197, 35, 47, 38, 187, 176, 30, 39, 130, 198, 36, 238, 52, 215, 36, 140, 222, 216, 38, 108, 224, 209, 42, 55, 191, 35, 180, 137, 137, 127, 212, 220, 182, 32, 215, 55, 49, 212, 43, 185, 123, 23, 111, 177, 220, 192, 125, 222, 218, 212, 16, 111, 38, 225, 46, 140, 187, 225, 43, 222, 224, 134, 123, 197, 47, 127, 198, 217, 214, 30, 194, 220, 52, 43, 65, 28, 227, 196, 215, 191, 228, 198, 138, 144, 196, 40, 222, 128, 145, 196, 128, 219, 137, 30, 130, 51, 190, 35, 221, 178, 216, 199, 222, 185, 143, 50, 220, 129, 187, 28, 182, 185, 192, 226, 218, 120, 208, 53, 52, 213, 135, 215, 197, 127, 123, 227, 131, 35, 139, 211, 131, 130, 128, 219, 31, 135, 194, 218, 43, 111, 187, 201, 225, 194, 140, 123, 117, 123, 51, 220, 43, 232, 127, 219, 234, 123, 27, 229, 199, 217, 197, 142, 128, 187, 52, 220, 47, 120, 214, 202, 128, 43, 123, 196, 222, 123, 143, 210, 135, 56, 209, 216, 222, 209, 192, 229, 129, 123, 111, 230, 180, 212, 43, 220, 142, 184, 208, 41, 22, 185, 123, 197, 230, 217, 129, 138, 204, 180, 55, 213, 189, 118, 231, 137, 32, 186, 143, 132, 129, 130, 45, 203, 118, 45, 137, 223, 44, 123, 227, 152, 47, 194, 213, 40, 142, 234, 191, 44, 220, 183, 122, 194, 36, 131, 208, 36, 123, 214, 217, 216, 133, 35, 184, 186, 128, 120, 217, 183, 128, 33, 212, 123, 200, 215, 135, 128, 191, 112, 124, 182, 212, 201, 182, 120, 210, 208, 192, 221, 199, 119, 224, 54, 182, 123, 139, 123, 127, 119, 185, 191, 199, 187, 192, 211, 45, 218, 43, 220, 214, 112, 216, 195, 194, 126, 212, 219, 148, 184, 209, 210, 198, 33, 49, 43, 200, 194, 43, 208, 35, 190, 213, 52, 135, 213, 50, 221, 227, 121, 203, 118, 197, 222, 199, 62, 132, 179, 196, 190, 216, 128, 192, 184, 208, 128, 19, 40, 221, 181, 186, 209, 233, 198, 18, 212, 221, 104, 47, 33, 141, 230, 124, 135, 95, 25, 35, 179, 189, 135, 116, 142, 181, 42, 208, 106, 227, 133, 43, 208, 210, 46, 184, 123, 196, 29, 33, 221, 220, 146, 210, 181, 123, 133, 127, 111, 124, 219, 220, 45, 118, 222, 128, 52, 226, 209, 214, 190, 176, 227, 211, 197, 40, 221, 217, 225, 33, 101, 221, 194, 196, 216, 226, 181, 220, 210, 214, 131, 219, 231, 55, 123, 129, 42, 50, 222, 188, 128, 215, 64, 39, 227, 192, 215, 140, 135, 196, 214, 230, 28, 135, 111, 194, 220, 190, 220, 199, 197, 179, 199, 50, 133, 199, 34, 158, 197, 135, 214, 226, 131, 227, 40, 47, 213, 223, 116, 225, 213, 13, 224, 209, 31, 129, 198, 221, 150, 181, 118, 211, 47, 211, 190, 222, 184, 30, 214, 48, 210, 125, 212, 183, 195, 216, 193, 43, 151, 182, 186, 216, 221, 144, 58, 221, 218, 237, 112, 41, 189, 184, 217, 137, 26, 188, 209, 222, 214, 131, 194, 43, 220, 200, 128, 40, 135, 155, 217, 208, 213, 31, 228, 183, 224, 33, 43, 226, 213, 196, 129, 149, 212, 181, 59, 181, 210, 196, 229, 133, 195, 109, 212, 33, 64, 211, 30, 230, 47, 191, 193, 214, 213, 132, 133, 43, 131, 182, 211, 227, 55, 216, 50, 106, 40, 225, 116, 220, 137, 212, 212, 54, 213, 121, 118, 219, 216, 219, 223, 208, 192, 184, 146, 184, 216, 198, 135, 226, 131, 118, 222, 198, 191, 125, 45, 137, 188, 51, 208, 133, 197, 184, 135, 44, 208, 201, 23, 217, 213, 215, 214, 215, 131, 209, 209, 38, 178, 221, 185, 214, 189, 229, 212, 214, 190, 47, 219, 219, 47, 143, 110, 209, 213, 230, 208, 193, 32, 52, 183, 46, 183, 209, 213, 112, 214, 208, 122, 211, 224, 191, 226, 208, 55, 208, 42, 18, 223, 192, 43, 181, 213, 200, 218, 217, 208, 216, 219, 35, 123, 122, 28, 125, 200, 186, 224, 58, 119, 23, 198, 209, 54, 40, 198, 192, 215, 229, 197, 132, 196, 198, 218, 195, 43, 122, 35, 210, 214, 122, 32, 19, 211, 49, 40, 185, 195, 210, 227, 214, 197, 219, 147, 208, 40, 7, 218, 45, 43, 215, 123, 200, 195, 43, 211, 214, 200, 217, 50, 194, 218, 211, 55, 186, 200, 36, 43, 139, 217, 54]

name = 'output2-{i:03d}.mid'
path = os.path.join('./', name)
n_notes = utils.event_indeces_to_midi_file(output, path)
print('===> {path} ({n_notes} notes)')


#========================================================================
# Settings
#========================================================================

def getopt():
    parser = optparse.OptionParser()

    parser.add_option('-c', '--control',
                      dest='control',
                      type='string',
                      default=None,
                      help=('control or a processed data file path, '
                            'e.g., "PITCH_HISTOGRAM;NOTE_DENSITY" like '
                            '"2,0,1,1,0,1,0,1,1,0,0,1;4", or '
                            '";3" (which gives all pitches the same probability), '
                            'or "/path/to/processed/midi/file.data" '
                            '(uses control sequence from the given processed data)'))

    parser.add_option('-b', '--batch-size',
                      dest='batch_size',
                      type='int',
                      default=8)

    parser.add_option('-s', '--session',
                      dest='sess_path',
                      type='string',
                      default='save/train.sess',
                      help='session file containing the trained model')

    parser.add_option('-o', '--output-dir',
                      dest='output_dir',
                      type='string',
                      default='output/')

    parser.add_option('-l', '--max-length',
                      dest='max_len',
                      type='int',
                      default=1000)

    parser.add_option('-g', '--greedy-ratio',
                      dest='greedy_ratio',
                      type='float',
                      default=1.0)

    parser.add_option('-B', '--beam-size',
                      dest='beam_size',
                      type='int',
                      default=0)

    parser.add_option('-T', '--temperature',
                      dest='temperature',
                      type='float',
                      default=1.0)

    parser.add_option('-z', '--init-zero',
                      dest='init_zero',
                      action='store_true',
                      default=False)

    return parser.parse_args()[0]


opt = getopt()

#------------------------------------------------------------------------

output_dir = opt.output_dir
sess_path = opt.sess_path
batch_size = opt.batch_size
max_len = opt.max_len
greedy_ratio = opt.greedy_ratio
control = opt.control
use_beam_search = opt.beam_size > 0
beam_size = opt.beam_size
temperature = opt.temperature
init_zero = opt.init_zero

if use_beam_search:
    greedy_ratio = 'DISABLED'
else:
    beam_size = 'DISABLED'

assert os.path.isfile(sess_path), f'"{sess_path}" is not a file'

if control is not None:
    if os.path.isfile(control) or os.path.isdir(control):
        if os.path.isdir(control):
            files = list(utils.find_files_by_extensions(control))
            assert len(files) > 0, f'no file in "{control}"'
            control = np.random.choice(files)
        _, compressed_controls = torch.load(control)
        controls = ControlSeq.recover_compressed_array(compressed_controls)
        if max_len == 0:
            max_len = controls.shape[0]
        controls = torch.tensor(controls, dtype=torch.float32)
        controls = controls.unsqueeze(1).repeat(1, batch_size, 1).to(device)
        control = f'control sequence from "{control}"'

    else:
        pitch_histogram, note_density = control.split(';')
        pitch_histogram = list(filter(len, pitch_histogram.split(',')))
        if len(pitch_histogram) == 0:
            pitch_histogram = np.ones(12) / 12
        else:
            pitch_histogram = np.array(list(map(float, pitch_histogram)))
            assert pitch_histogram.size == 12
            assert np.all(pitch_histogram >= 0)
            pitch_histogram = pitch_histogram / pitch_histogram.sum() \
                              if pitch_histogram.sum() else np.ones(12) / 12
        note_density = int(note_density)
        assert note_density in range(len(ControlSeq.note_density_bins))
        control = Control(pitch_histogram, note_density)
        controls = torch.tensor(control.to_array(), dtype=torch.float32)
        controls = controls.repeat(1, batch_size, 1).to(device)
        control = repr(control)

else:
    controls = None
    control = 'NONE'

assert max_len > 0, 'either max length or control sequence length should be given'

#------------------------------------------------------------------------

print('-' * 70)
print('Session:', sess_path)
print('Batch size:', batch_size)
print('Max length:', max_len)
print('Greedy ratio:', greedy_ratio)
print('Beam size:', beam_size)
print('Output directory:', output_dir)
print('Controls:', control)
print('Temperature:', temperature)
print('Init zero:', init_zero)
print('-' * 70)


#========================================================================
# Generating
#========================================================================

state = torch.load(sess_path)
model = PerformanceRNN(**state['model_config']).to(device)
model.load_state_dict(state['model_state'])
model.eval()
print(model)
print('-' * 70)

if init_zero:
    init = torch.zeros(batch_size, model.init_dim).to(device)
else:
    init = torch.randn(batch_size, model.init_dim).to(device)

with torch.no_grad():
    if use_beam_search:
        outputs = model.beam_search(init, max_len, beam_size,
                                    controls=controls,
                                    temperature=temperature,
                                    verbose=True)
    else:
        outputs = model.generate(init, max_len,
                                controls=controls,
                                greedy=greedy_ratio,
                                temperature=temperature,
                                verbose=True)

outputs = outputs.cpu().numpy().T # [batch, steps]


#========================================================================
# Saving
#========================================================================

os.makedirs(output_dir, exist_ok=True)

for i, output in enumerate(outputs):

    name = f'output-{i:03d}.mid'
    path = os.path.join(output_dir, name)
    n_notes = utils.event_indeces_to_midi_file(output, path)
    print(f'===> {path} ({n_notes} notes)')
