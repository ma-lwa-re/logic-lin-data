'''
MIT License

Copyright (c) 2022 ma-lwa-re

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, ChoicesSetting


class LinData(HighLevelAnalyzer):
    '''
    High-level extension for the LIN protocol.
    '''

    LIN_DATA_FIRST = 0
    LIN_DATA_LAST  = 7

    data = {}
    start_time = None
    protected_id = None
    number_display = ChoicesSetting(choices=("Decimal", "Hexadecimal"))
    terminal_display = ChoicesSetting(choices=("CSV", "Plain"))

    result_types = {
        "data": {
            "format": "{{type}}: {{data.data}}"
        },
        "header_pid": {
            "format": "PID: {{data.protected_id}}"
        }
    }

    def __init__(self):
        '''
        Initialize LinData.
        '''

        # If terminal display is CSV, display the header in the terminal
        if self.terminal_display == "CSV":
            print("datetime,protected_id,0,1,2,3,4,5,6,7")

    def decode(self, frame: AnalyzerFrame):
        '''
        Process a frame from the input analyzer, and optionally return a single
        `AnalyzerFrame`. The type and data values in `frame` will depend on the
        LIN analyzer.
        '''

        if frame.type == "data":
            if self.number_display == "Hexadecimal":
                self.data[frame.data["index"]] = hex(frame.data["data"])
            else:
                self.data[frame.data["index"]] = frame.data["data"]

            if frame.data["index"] == self.LIN_DATA_FIRST:
                self.start_time = frame.start_time
            if frame.data["index"] != self.LIN_DATA_LAST:
                return

            if self.terminal_display == "CSV":
                print(self.start_time.__str__() + "," + str(self.protected_id) + "," +
                    ",".join([str(frame_value) for frame_value in self.data.values()])
                )
            else:
                print(self.start_time.__str__(), str(self.protected_id), self.data)

            return AnalyzerFrame(frame.type, self.start_time, frame.end_time, {
	            "data": str(self.data),
	            "protected_id": self.protected_id,
	            "index": frame.data["index"]
            })

        if frame.type == "header_pid":
            self.data = {}
            self.protected_id = frame.data["protected_id"]

            return AnalyzerFrame(frame.type, frame.start_time, frame.end_time, {
	            "protected_id": self.protected_id
            })
