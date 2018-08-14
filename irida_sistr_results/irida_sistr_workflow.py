import uuid


class IridaSistrWorkflow:
    """Functionality for conversion between workflow ids and versions."""

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
    def workflow_versions_to_ids(cls, workflow_versions):
        """
        Converts a list of IRIDA workflow versions to a list of ids.
        :param workflow_versions: The list of workflow versions.
        :return: The list of ids.
        """
        return None if workflow_versions is None else [cls.workflow_version_to_id(x) for x in workflow_versions]

    @classmethod
    def workflow_ids_or_versions_to_ids(cls, workflow_versions_or_ids):
        """
        Converts a list of IRIDA workflow versions or ids to a list of ids.
        :param workflow_versions: The list of workflow versions or ids.
        :return: The list of workflow ids.
        """
        if workflow_versions_or_ids is None:
            return None
        else:
            ids_list = []
            for value in workflow_versions_or_ids:
                try:
                    id = uuid.UUID('{' + value + '}')
                    ids_list.append(str(id))
                except ValueError:
                    id = cls.workflow_version_to_id(value)
                    ids_list.append(id)

            return ids_list

    @classmethod
    def all_workflow_versions(cls):
        """
        Gets a list of all workflow versions.
        :return: A list of all workflow versions.
        """
        versions = list(cls.WORKFLOW_VERSIONS.values())
        versions.remove(None)
        return versions
