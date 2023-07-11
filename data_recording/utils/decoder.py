class PayloadDecoder:
    """
    Handles HCB roi data
    The hex String for the ROIs is calculated in different manners, depending on the sensor type!
    """

    @staticmethod
    def __decode_thermal(roi_values: str) -> list:
        """ 1 count equals 0.25°C beginning at 10°:
            "5A61704E"  =  0: 0x5A, 1: 0x61,  2: 0x70, 3: 0x4E ...
            -> in decimal  0: 90,   1: 97,    2: 112,  3: 78   ...
            -> in °C       0: 32.5, 1: 34.25, 2: 38.0, 3: 29.5 ..."""
        # Step 1: unpacking the string in two lists of equal length
        # Step 2: zip the two lists into a list of tuples [(x_0,y_0),(x_1,y_1)...,(x_n,y_n)]
        # Step 3: transform into decimal
        # Step 4: transform value into right unit
        roi_values = [int(x + y, 16) * .25 + 10 for x, y in zip(roi_values[::2], roi_values[1::2])]
        return roi_values

    @staticmethod
    def __decode_tof(roi_values: str) -> list:
        """ 1 count equals 2cm distance form the sensor to the object:
            "5A61704E" =   0: 0x5A, 1: 0x61, 2: 0x70, 3: 0x4E
            -> in decimal  0: 90,   1: 97,   2: 112,  3: 78
            -> in cm       0: 180,  1: 194,  2: 224,  3: 156"""
        # Step 1: unpacking the string in two lists of equal length
        # Step 2: zip the two lists into a list of tuples [(x_0,y_0),(x_1,y_1)...,(x_n,y_n)]
        # Step 3: transform into decimal
        # Step 4: transform value into right unit
        roi_values = [int(x + y, 16) * 2 for x, y in zip(roi_values[::2], roi_values[1::2])]
        return roi_values

    @staticmethod
    def __decode_accel(hcb_data) -> list:
        return [float(hcb_data['accelerometer_x']) / 1000, float(hcb_data['accelerometer_y']) / 1000,
                float(hcb_data['accelerometer_z']) / 1000]

    def decode_payload(self, hcb_data: dict) -> dict:
        return_dict = {}
        if 'type' in hcb_data.keys():  # Thermal packet
            if hcb_data['type'] == 'THERMAL_ROI':
                return_dict['thermal_readings'] = self.__decode_thermal(hcb_data['roi'])
            elif hcb_data['type'] == 'ToF_ROI':
                return_dict['tof_readings'] = self.__decode_tof(hcb_data['roi'])
        elif 'roi_values' in hcb_data.keys():  # idle packet
            if len(hcb_data['roi_values']):  # 8x8 has empty string
                return_dict['tof_readings'] = self.__decode_tof(hcb_data['roi_values'])
            return_dict['accel_vector'] = self.__decode_accel(hcb_data)
        elif 'roi' in hcb_data.keys():  # old thermal packet
            return_dict['thermal_readings'] = self.__decode_thermal(hcb_data['roi'])
        if len(return_dict.keys()):
            return return_dict
        raise ValueError(f'Invalid payload: {hcb_data}')
