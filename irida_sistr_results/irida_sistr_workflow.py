"""
Functionality for conversion between workflow ids and versions.
"""


class IridaSistrWorkflow:
    WORKFLOW_IDS = {
        '0.1': 'e559af58-a560-4bbd-997e-808bfbe026e2',
        '0.1.0': 'e559af58-a560-4bbd-997e-808bfbe026e2',
        '0.2': 'e8f9cc61-3264-48c6-81d9-02d9e84bccc7',
        '0.2.0': 'e8f9cc61-3264-48c6-81d9-02d9e84bccc7',
        '0.3': '92ecf046-ee09-4271-b849-7a82625d6b60',
        '0.3.0': '92ecf046-ee09-4271-b849-7a82625d6b60',
        None: None
    }
    WORKFLOW_VERSIONS = {
        'e559af58-a560-4bbd-997e-808bfbe026e2': '0.1',
        'e8f9cc61-3264-48c6-81d9-02d9e84bccc7': '0.2',
        '92ecf046-ee09-4271-b849-7a82625d6b60': '0.3',
        None: None
    }

    @classmethod
    def workflow_id_to_version(cls, workflow_id):
        """
        Converts an IRIDA workflow id to a version number.
        :param workflow_id: The workflow id.
        :return: The version number for the workflow.
        """
        return cls.WORKFLOW_VERSIONS[workflow_id]

    @classmethod
    def workflow_version_to_id(cls, workflow_version):
        """
        Converts an IRIDA workflow version to an id.
        :param workflow_version: The workflow version.
        :return: The id of the workflow.
        """
        return cls.WORKFLOW_IDS[workflow_version]

    @classmethod
    def all_workflow_versions(cls):
        """
        Gets a list of all workflow versions.
        :return: A list of all workflow versions.
        """
        versions = list(cls.WORKFLOW_VERSIONS.values())
        versions.remove(None)
        return versions
