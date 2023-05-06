from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt

from Model.Model import Model
from View.ui.companiesWindow_ui import Ui_companiesWindow

class CompaniesWindow(QtWidgets.QWidget):
    def __init__(self, model: Model, main_window: QtWidgets.QMainWindow):
        super(CompaniesWindow, self).__init__()
        self.ui = Ui_companiesWindow()
        self.ui.setupUi(self)
        self.model = model
        self.main_window = main_window

        self.ui.addCompanyButton.clicked.connect(self.AddCompanyHandler)
        self.ui.addDomainButton.clicked.connect(self.AddDomainHandler)
        self.ui.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.treeView.customContextMenuRequested.connect(self.TreeViewMenuHandler)

        self.UpdateInfo()
    
    def UpdateInfo(self):
        companies = self.model.dataStorage.get_companies_domains()
        self.DownloadTreeView(companies)
        self.ui.CompanyDomainComboBox.clear()
        self.SetComboBoxCompanies(companies)
        self.main_window.UpdateData()

    def DownloadTreeView(self, companies: list[dict]):
        self.modelTree = QtGui.QStandardItemModel()
        self.modelTree.setHorizontalHeaderLabels(['Компании'])
        for company in companies:
            company_item = QtGui.QStandardItem(company["name"] + " - " + company["type"])
            company_item.setData(["company", company["id"]])
            for domain in company["domains"]:
                if domain[0] is None and domain[1] is None:
                    continue
                domain_item = QtGui.QStandardItem(domain[1])
                domain_item.setData(["domain", domain[0]])
                company_item.setChild(company_item.rowCount(), 0, domain_item)
            company_item.sortChildren(0, Qt.AscendingOrder)
            self.modelTree.appendRow([company_item])

        self.modelTree.sort(0, Qt.AscendingOrder)
        self.ui.treeView.setModel(self.modelTree)
    
    def SetComboBoxCompanies(self, companies: list[dict]):
        index = 0
        for company in companies:
            self.ui.CompanyDomainComboBox.addItem(company["name"])
            self.ui.CompanyDomainComboBox.setItemData(index, {"id": company["id"]})
            index += 1
    
    def AddCompanyHandler(self):
        company_name = self.ui.companyNameEdit.text()
        company_type = self.ui.companyTypeComboBox.currentText()
        try:
            self.model.dataStorage.add_company(company_name, company_type)
        except Exception as error:
            self.main_window.ShowError(str(error))
        self.UpdateInfo()
    
    def AddDomainHandler(self):
        domain_name = self.ui.DomainEdit.text()
        index = self.ui.CompanyDomainComboBox.currentIndex()
        company_id = self.ui.CompanyDomainComboBox.itemData(index).get("id", None)
        try:
            self.model.dataStorage.add_domain(domain_name, company_id)
        except Exception as error:
            self.main_window.ShowError(str(error))
        self.UpdateInfo()

    def TreeViewMenuHandler(self, pos):
        indexes = self.ui.treeView.selectedIndexes()
        if indexes:
            menu = QtWidgets.QMenu()
            delete_action = QtWidgets.QAction("Удалить", self.ui.treeView)
            menu.addAction(delete_action)
            action = menu.exec_(self.ui.treeView.viewport().mapToGlobal(pos))
            if action == delete_action:
                index = self.ui.treeView.indexAt(pos)
                if not index.isValid():
                    return
                data = self.modelTree.itemFromIndex(index).data()
                try:
                    if data[0] == "company":
                        self.model.dataStorage.del_company(data[1])
                    elif data[0] == "domain":
                        self.model.dataStorage.del_domain(data[1])
                except Exception as error:
                    self.main_window.ShowError(str(error))
                self.UpdateInfo()
                
