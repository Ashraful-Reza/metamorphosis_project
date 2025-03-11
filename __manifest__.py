{
    'name': 'Employee Profile PDF Report Print',
    'version': '15.0.1.0',
    'category': 'Human Resources',
    'summary': """
    Enhance the Employee Profile in Odoo HR with additional records for nominees,
    children, training, and emergency contacts. Easily manage and print a comprehensive 
    employee profile summary as a PDF.""",

    'description': """
    The Employee Profile PDF Report Print module extends the Odoo HR module by introducing 
    new sections for enhanced employee information management. Users can now add and maintain:
    Nominee Records (Name, Relation, Address, Photograph)
    Child Records (Name, Date of Birth, Photograph)
    Training Records (Training Title, Year, Institution)
    Emergency Contact Details (Name, Telephone, Mobile, Address)

    These sections are available as new pages in the employee form view, allowing seamless data entry.
     Additionally, the module enables users to generate and print an Employee Profile Summary as a 
     well-structured PDF report for documentation or administrative use.
    This module enhances HR data management, ensuring critical employee details are well-documented and easily accessible.
        
    """,
    'author':"Metamorphosis Ltd, Tanjil",
    'co-author':"Tanjil",
    'website':'https://metamorphosis.com.bd',
    'depends': ['base', 'hr','hr_skills'],
    'data': [
        'security/ir.model.access.csv', 
        'views/employee_views.xml',   
        'views/hr_resume_views.xml',   
        'views/hr_employee_views.xml',   
        'views/hr_employee_child_views.xml',   
        'views/hr_employee_training_views.xml',   
        'views/hr_employee_emergency_views.xml',   
        'report/employee_report.xml',    
        'report/employee_templates.xml',
    ],
    'license': 'LGPL-3',
     "sequence" : -50,
    'installable': True,
    'application': True,
    "auto_install" : False,
    
}
