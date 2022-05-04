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

    DECIMAL = "Decimal"
    HEXADECIMAL = "Hexadecimal"
    CSV = "CSV"
    PLAIN = "Plain"

    data = {}
    start_time = None
    protected_id = None
    number_display = ChoicesSetting(choices=(DECIMAL, HEXADECIMAL))
    terminal_display = ChoicesSetting(choices=(CSV, PLAIN))

    result_types = {
        "data": {
            "format": "DATA: {{data.data}}"
        },
        "checksum": {
            "format": "CHK: {{data.checksum}}"
        },
        "header_pid": {
            "format": "PID: {{data.protected_id}}"
        }
    }

    def __init__(self):
        '''
        Initialize LinData.
        '''

        # If terminal display is CSV, print the header in the terminal
        if self.terminal_display == self.CSV:
            print("datetime,protected_id,0,1,2,3,4,5,6,7,checksum")

    def decode(self, frame: AnalyzerFrame):
        '''
        Process a frame from the input analyzer, and optionally return a single
        `AnalyzerFrame`. The type and data values in `frame` will depend on the
        LIN analyzer.
        '''

        if frame.type == "data":
            self.data[frame.data["index"]] = frame.data["data"]

            if self.number_display == self.HEXADECIMAL:
                self.data[frame.data["index"]] = f"0x{frame.data['data']:02X}"

            if not self.start_time:
                self.start_time = frame.start_time

            return AnalyzerFrame(frame.type, self.start_time, frame.end_time, {
                "data": ", ".join([str(frame_value) for frame_value in self.data.values()]),
                "protected_id": self.protected_id,
                "index": frame.data["index"]
            })

        elif "checksum" in frame.type:
            checksum = frame.data["checksum"]

            if self.number_display == self.HEXADECIMAL:
                checksum = f"0x{frame.data['checksum']:02X}"

            if self.terminal_display == self.CSV:
                csv_data = {0: "", 1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: ""}
                for i, _ in enumerate(csv_data):
                    try:
                        csv_data[i] = self.data[i]
                    except KeyError:
                        continue

                print(self.start_time.__str__() + "," + str(self.protected_id) + "," +
                      ",".join([str(frame_value) for frame_value in csv_data.values()]) +
                      "," + str(checksum))
            else:
                print(self.start_time.__str__(), str(self.protected_id), self.data, checksum)

            return AnalyzerFrame("checksum", frame.start_time, frame.end_time, {
                "checksum": checksum
            })

        elif frame.type == "header_pid":
            self.data = {}
            self.start_time = None
            self.protected_id = frame.data["protected_id"]

            if self.number_display == self.HEXADECIMAL:
                self.protected_id = f"0x{frame.data['protected_id']:02X}"

            return AnalyzerFrame(frame.type, frame.start_time, frame.end_time, {
                "protected_id": self.protected_id
            })
