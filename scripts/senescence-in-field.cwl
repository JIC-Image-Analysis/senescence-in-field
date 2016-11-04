cwlVersion: v1.0
class: CommandLineTool
baseCommand: /scripts/analysis.py
inputs:
    input_file:
        type: string
        inputBinding:
            position: 1
    output_dir:
        type: string
        inputBinding:
            position: 2
outputs: []
