from pathlib import Path
import pdb
import json
import os

from PySide6.QtGui import QColor #for colors
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QHeaderView,
    QFileDialog,
    QTreeWidget,
    QTreeWidgetItem,
    QListWidget,
    QListWidgetItem
)
from qt_material import apply_stylesheet

from loadConfig import Configs
cfgLoader = Configs()
CONFIG = cfgLoader.loadGlobalConfig

from packetDefinitionLib import PacketDefinitionUtility

STRUCTUREBASECOLOR = (70,125,255)
ERRORCOLOR = QColor.fromHsv(0,255,255)
WHITE = QColor.fromHsv(0,0,255)
typeOptions = {
            "uint":{"label":"manually-sized uint","size":0},
            "uint8_t":{"label":"8-bit unsigned int","size":8},
            "uint16_t":{"label":"16-bit unsigned int","size":16},
            "uint32_t":{"label":"32-bit unsigned int","size":32},
            "uint64_t":{"label":"64-bit unsigned int","size":64},
            "uint128_t":{"label":"128-bit unsigned int","size":128},
            "int":{"label":"manually-sized int","size":0},
            "int8_t":{"label":"8-bit signed int","size":8},
            "int16_t":{"label":"16-bit signed int","size":16},
            "int32_t":{"label":"32-bit signed int","size":32},
            "int64_t":{"label":"64-bit signed int","size":64},
            "int128_t":{"label":"128-bit signed int","size":128},
            "float":{"label":"float","size":32},
            "double":{"label":"double","size":64},
            "char":{"label":"char","size":8}
        }

def colorGen(baseColor, hueStep=55):
    while True:
        yield QColor.fromHsv(*baseColor)
        baseColor = ((baseColor[0] + hueStep) % 360, baseColor[1], baseColor[2])


class FieldItem(QTreeWidgetItem):
    def __init__(self,treeWidget,sourceFile,fieldDict,color):
        super().__init__(treeWidget,[fieldDict['fieldName']])
        self.fieldDict = fieldDict
        self.validator = PacketDefinitionUtility()
        validField,msgs = self.validator.validateField(fieldDict)
        
        if 'conversion' in fieldDict:
            self.conversion = fieldDict['conversion']
        else:
            self.conversion = None
        if 'limits' in fieldDict:
            self.limits = fieldDict['limits']
        else:
            self.limits = None

        if validField:
            self.setBackground(0,color)
        else:
            self.setBackground(0,ERRORCOLOR)
            pdb.set_trace()

    def changeAllParentsColor(self):
        pass

class PacketDefinitionEditor(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Packet Definition Editor")
        mainGuiPath = Path('ui')
        mainGuiPath = mainGuiPath / 'packetDefinitionBuilder.ui'

        self.pktDefUtil = PacketDefinitionUtility()

        ui_file = QFile(mainGuiPath)
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        ui_file.close()
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        
        #apply_stylesheet(self.window, theme=CONFIG()['guiTheme'])
        self.ui.show()
        self.initGUI()
    
    def initGUI(self):
        self.ui.telemetryDefinitionsTree.setHeaderHidden(True)
        self.ui.telemetryDefinitionsTree.setColumnCount(1)
        self.ui.structureTree.setHeaderHidden(True)
        self.ui.structureTree.setColumnCount(1)
        self.ui.fieldsTree.setHeaderHidden(True)
        self.ui.fieldsTree.setColumnCount(1)
        self.loadDefsStructs()
        self.ui.structureTree.itemSelectionChanged.connect(self.structureSelected)
        self.ui.telemetryDefinitionsTree.itemSelectionChanged.connect(self.telemetryDefinitionSelected)
        self.ui.fieldsTree.itemSelectionChanged.connect(self.fieldSelected)
        
        #fields signals
        self.ui.dataTypeComboBox.currentTextChanged.connect(self.dataTypeSelected)

        self.ui.variableLengthCheckbox.stateChanged.connect(self.variableLengthChanged)
        self.ui.arrayLengthSpinBox.valueChanged.connect(self.arrayLengthChanged)
        self.ui.saveDefinitionButton.clicked.connect(self.saveTelemetryDefinitions)
        self.ui.dynamicLengthFieldButton.setEnabled(False)
        self.ui.dynamicLengthFieldLineEdit.setEnabled(False)
        self.ui.lengthFieldOffsetSpinBox.setEnabled(False)
        self.ui.lengthInBitsComboBox.setEnabled(False)

        self.fieldControls = [
            self.ui.fieldNameLineEdit,
            self.ui.dataTypeComboBox,
            self.ui.descriptionTextEdit,
            self.ui.arrayLengthSpinBox,
            self.ui.variableLengthCheckbox,
            self.ui.dynamicLengthFieldButton,
            self.ui.dynamicLengthFieldLineEdit,
            self.ui.lengthFieldOffsetSpinBox,
            self.ui.lengthInBitsComboBox,
            self.ui.bitLengthSpinBox
        ]
        self.ui.fieldNameLineEdit.onTextChanged.connect(lambda: self.writeDefDict(self.ui.fieldsTree.selectedItems()[0]))
        

    def loadDefsStructs(self):
        self.populateTelemetryDefinitions()
        self.validateAllTelemetryDefinitions()
        self.populateTelemetryStructures()

    def populateTelemetryDefinitions(self):
        self.ui.telemetryDefinitionsTree.clear()
        tdefPath = Path(CONFIG()['telemetryDefinitionsBasepath'])

        files = [f for f in tdefPath.rglob('*') if f.is_file() and f.suffix in ('.hd')]
        self.telemetryDefinitions = {}

        for telemetryDefinitionFile in files:
            self.telemetryDefinitions[telemetryDefinitionFile.name] = json.load(open(telemetryDefinitionFile,'r'))
            item = QTreeWidgetItem(self.ui.telemetryDefinitionsTree,[telemetryDefinitionFile.name])            
            
        files = [f for f in tdefPath.rglob('*') if f.is_file() and f.suffix in ('.pd')]
        for telemetryDefinitionFile in files:
            self.telemetryDefinitions[telemetryDefinitionFile.name] = json.load(open(telemetryDefinitionFile,'r'))
            packetDefinition = self.telemetryDefinitions[telemetryDefinitionFile.name]
            item = QTreeWidgetItem(self.ui.telemetryDefinitionsTree,[telemetryDefinitionFile.name])
            for k in packetDefinition.keys():
                packetName = packetDefinition[k]['packetName']
                packetItem = QTreeWidgetItem(item,[f"{k} - {packetName}"])

    def populateTelemetryStructures(self):
        self.ui.structureTree.clear()
        colorGenerator = colorGen(STRUCTUREBASECOLOR)
        for structureName, structure in CONFIG()['telemetryStructures'].items():
            item = QTreeWidgetItem([structureName])
            self.ui.structureTree.addTopLevelItem(item)
            for path in structure['format']:
                fname = Path(path).name
                component = QTreeWidgetItem([fname])
                item.addChild(component)
                component.setBackground(0,next(colorGenerator))

    def validateAllTelemetryDefinitions(self):
        pdb.set_trace()
        for i in range(self.ui.telemetryDefinitionsTree.topLevelItemCount()):
            validDefinition = True
            telemetryDefItem = self.ui.telemetryDefinitionsTree.topLevelItem(i)
            telemetryDefName = telemetryDefItem.text(0)
            telemetryDefDict = self.telemetryDefinitions[telemetryDefName]
            if 'fields' in telemetryDefDict:
                for field in telemetryDefDict['fields']:
                    validField, msgs = self.pktDefUtil.validateField(field)
                    if not validField:
                        validDefinition = False
                        telemetryDefItem.setBackground(0,ERRORCOLOR)
            else:
                for id,packet in telemetryDefDict.items():
                    if 'fields'in packet:
                        for field in packet['fields']:
                            validField, msgs = self.pktDefUtil.validateField(field,telemetryDefName)
                            if not validField:
                                validDefinition = False
                                telemetryDefItem.setBackground(0,ERRORCOLOR)
                        
    def structureSelected(self):
        self.ui.fieldsTree.clear()
        selectedItems = self.ui.structureTree.selectedItems()
        if selectedItems:
            selectedItem = selectedItems[0]
            parentItem = selectedItem.parent()
            if parentItem:
                structureItem = parentItem
            else:
                structureItem = selectedItem
            
            childCount = structureItem.childCount()
            for i in range(childCount):
                childItem = structureItem.child(i)
                childText = childItem.text(0)
                childColor = childItem.background(0).color()
                defDict = self.telemetryDefinitions[childText]
                if 'fields' in defDict:
                    fieldsList = defDict['fields']
                    self.populateFields(fieldsList,childText,self.ui.fieldsTree,childColor)
                else:
                    #packet definition
                    for pktId,pktDef in defDict.items():
                        packetItem = QTreeWidgetItem(self.ui.fieldsTree,[f"{pktId} - {pktDef['packetName']}"])
                        packetItem.setBackground(0,childColor)
                        self.populateFields(pktDef['fields'],childText,packetItem,childColor)
    
    def telemetryDefinitionSelected(self):
        self.ui.fieldsTree.clear()
        selectedItems = self.ui.telemetryDefinitionsTree.selectedItems()
        if selectedItems:
            selectedItem = selectedItems[0]
            parentItem = selectedItem.parent()
            if parentItem:
                #packet in telemetry definition selected, show fields for that packet
                telemetryDefinitionName = parentItem.text(0)
                selectedKeyString = selectedItem.text(0).split(' - ')[0]
                defDict = self.telemetryDefinitions[telemetryDefinitionName][selectedKeyString]
                self.populateFields(defDict['fields'],telemetryDefinitionName,self.ui.fieldsTree)
            else:
                defDict = self.telemetryDefinitions[selectedItem.text(0)]
                telemetryDefinitionName = selectedItem.text(0)
                if not 'fields' in defDict:
                    #packet definition selected, display all packets
                    
                    for pktId,pktDef in defDict.items():
                        packetItem = QTreeWidgetItem(self.ui.fieldsTree,[f"{pktId} - {pktDef['packetName']}"])
                        self.populateFields(pktDef['fields'],telemetryDefinitionName,packetItem)
                else:
                    #header definition selected, simply show all fields
                    defDict = self.telemetryDefinitions[telemetryDefinitionName]
                    self.populateFields(defDict['fields'],telemetryDefinitionName,self.ui.fieldsTree)
    
    def fieldSelected(self):
        selectedItems = self.ui.fieldsTree.selectedItems()
        if selectedItems:
            selectedItem = selectedItems[0]

        if len(selectedItems) > 0 and isinstance(selectedItem,FieldItem):
            fieldDict = selectedItem.fieldDict
            self.populateFieldParameters(fieldDict)

    def variableLengthChanged(self,state):
        if state == 2:
            self.ui.dynamicLengthFieldButton.setEnabled(True)
            self.ui.dynamicLengthFieldLineEdit.setEnabled(True)
            self.ui.lengthFieldOffsetSpinBox.setEnabled(True)
            self.ui.lengthInBitsComboBox.setEnabled(True)
            self.ui.arrayLengthSpinBox.setEnabled(False)
            self.ui.bitLengthSpinBox.setEnabled(False)
        else:
            self.ui.dynamicLengthFieldButton.setEnabled(False)
            self.ui.dynamicLengthFieldLineEdit.setEnabled(False)
            self.ui.lengthFieldOffsetSpinBox.setEnabled(False)
            self.ui.lengthInBitsComboBox.setEnabled(False)
            self.ui.arrayLengthSpinBox.setEnabled(True)
            self.ui.bitLengthSpinBox.setEnabled(True)

    def dataTypeSelected(self,text):
        if text == "manually-sized uint" or text == "manually-sized int":
            self.ui.bitLengthSpinBox.setEnabled(True)
        else:
            self.setBitLength()

    def arrayLengthChanged(self):
        self.setBitLength()

    def setBitLength(self):
        typeText = self.ui.dataTypeComboBox.currentText()
        for typeName, typeDict in typeOptions.items():
            if typeText == typeDict['label']:
                arrayLength = self.ui.arrayLengthSpinBox.value()
                bitLength = typeDict['size'] * arrayLength
                self.ui.bitLengthSpinBox.setValue(bitLength)
                break
        self.ui.bitLengthSpinBox.setEnabled(False)

    def populateFields(self,fieldsList,sourceFile,parent,color=QColor.fromHsv(0,0,255)):
        for fieldDict in fieldsList:
            FieldItem(parent,sourceFile,fieldDict,color)

    def populateFieldParameters(self,fieldDict):
        validField, msgs = self.pktDefUtil.validateField(fieldDict)
        if not validField:
            self.ui.validFieldLabel.setText(f"Invalid Field")
            self.ui.validFieldLabel.setStyleSheet("color:red")
            errors = "\n".join(msgs)
            self.ui.fieldMessages.setText(errors)
        else:
            self.ui.validFieldLabel.setText(f"Valid Field")
            self.ui.validFieldLabel.setStyleSheet("color:green")
            self.ui.fieldMessages.setText("Field fully validated")
        self.ui.fieldNameLineEdit.setText(fieldDict['fieldName'])
        
        typeOptions = {
            "uint":{"label":"manually-sized uint","size":0},
            "uint8_t":{"label":"8-bit unsigned int","size":8},
            "uint16_t":{"label":"16-bit unsigned int","size":16},
            "uint32_t":{"label":"32-bit unsigned int","size":32},
            "uint64_t":{"label":"64-bit unsigned int","size":64},
            "uint128_t":{"label":"128-bit unsigned int","size":128},
            "int":{"label":"manually-sized int","size":0},
            "int8_t":{"label":"8-bit signed int","size":8},
            "int16_t":{"label":"16-bit signed int","size":16},
            "int32_t":{"label":"32-bit signed int","size":32},
            "int64_t":{"label":"64-bit signed int","size":64},
            "int128_t":{"label":"128-bit signed int","size":128},
            "float":{"label":"float","size":32},
            "double":{"label":"double","size":64},
            "char":{"label":"char","size":8}
        }

        parameterDict = typeOptions[fieldDict['type']] 
        self.ui.dataTypeComboBox.setCurrentText(parameterDict['label'])
        if 'description' in fieldDict:
            self.ui.descriptionTextEdit.setPlainText(fieldDict['description'])
        if 'arrayLength' in fieldDict:
            self.ui.arrayLengthSpinBox.setValue(fieldDict['arrayLength'])
        else:
            self.ui.arrayLengthSpinBox.setValue(1)

        if 'variableLength' in fieldDict:
            self.ui.variableLengthCheckbox.setChecked(True)
            self.ui.dynamicLengthFieldLineEdit.setText(fieldDict['variableLength']['lengthField'])
            self.ui.lengthFieldOffsetSpinBox.setValue(fieldDict['variableLength']['lengthFieldOffset'])
            if fieldDict['variableLength']['lengthInBits']:
                self.ui.lengthInBitsComboBox.setCurrentText("Bits")
            else:                
                self.ui.lengthInBitsComboBox.setCurrentText("Bytes")
        
        if self.ui.dataTypeComboBox.currentText() != "manually-sized uint" and self.ui.dataTypeComboBox.currentText() != "manually-sized int":
            self.ui.bitLengthSpinBox.setValue(parameterDict['size'] * self.ui.arrayLengthSpinBox.value())
        else:
            if 'bitLength' in fieldDict:
                self.ui.bitLengthSpinBox.setValue(fieldDict['bitLength'])
            else:
                self.ui.bitLengthSpinBox.setValue(0)

        if not validField:
            for control in self.fieldControls:
                control.setEnabled(True)

    def writeDefDict(self,item):
        fieldDict ={}
        fieldDict['fieldName'] = self.ui.fieldNameLineEdit.text()
        fieldDict['bitLength'] = self.ui.bitLengthSpinBox.value()
        for typeName, typeDict in typeOptions.items():
            if self.ui.dataTypeComboBox.currentText() == typeDict['label']:
                fieldDict['type'] = typeName
                break
        
        if len(self.ui.descriptionTextEdit.toPlainText()) > 0:
            fieldDict['description'] = self.ui.descriptionTextEdit.toPlainText()
        
        if self.ui.arrayLengthSpinBox.value() > 1:
            fieldDict['arrayLength'] = self.ui.arrayLengthSpinBox.value()

        if self.ui.variableLengthCheckbox.isChecked():
            fieldDict['variableLength'] = {
                'lengthField': self.ui.dynamicLengthFieldLineEdit.text(),
                'lengthFieldOffset': self.ui.lengthFieldOffsetSpinBox.value(),
                'lengthInBits': self.ui.lengthInBitsComboBox.currentText() == "Bits"
            }
        else:
            fieldDict['bitstructType'] = self.pktDefUtil.getBitstructType(fieldDict)
        
        if item.conversion:
            fieldDict['conversion'] = item.conversion
        if item.limits:
            fieldDict['limits'] = item.limits

        item.fieldDict = fieldDict

    def saveTelemetryDefinitions(self):
        pdb.set_trace()
        for fileName, telemetryDef in self.telemetryDefinitions.items():
            savePath = Path(CONFIG()['telemetryDefinitionsBasepath']) / fileName
            with open(savePath,'w') as f:
                json.dump(telemetryDef,f,indent=4)
        



if __name__ == '__main__':
    os.environ.pop("SESSION_MANAGER", None)
    app = QApplication([])
    editor = PacketDefinitionEditor()
    app.exec()