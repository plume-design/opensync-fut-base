"""Module used to prepare the testcase execution recipe.

Recipe can be used for manual execution of the testcase and it can also serve
for reference about the steps executed during the testcase execution.
Recipe is a list of strings.
"""


class Recipe:
    """Recipe class."""

    def __init__(self):
        self.recipe = []
        self.recipe_setup = []

    def add(self, device=None, cmd=None, start_t=None, end_t=None, ec=None):
        """Append dictionary to the recipe.

        Dictionary is containing information about the command executed
        during the test run.
        """
        self.recipe.append({
            'device': device,
            'cmd': cmd,
            'start_t': start_t,
            'end_t': end_t,
            'ec': ec,
        })

    def add_setup(self):
        """Add the current recipe list to the setup recipe.

        Current recipe is containing the information about the commands
        executed so far to the setup recipe list.

        It empties the recipe list afterwards.
        """
        self.recipe_setup += self.recipe
        self.recipe = []

    def clear(self):
        """Clear list with the command information.

        List contains the information about the command executed during the
        test run.
        Method is called during the client and REF device setup.
        """
        self.recipe = []

    def clear_full(self):
        """Clear the current recipe lists.

        Both lists are cleared (regular and setup recipe). Recipes are
        containing the information about the commands executed so far.

        Method is called once per session.
        """
        self.recipe = []
        self.recipe_setup = []

    def get_for_allure(self):
        """Merge the setup recipe list and the recipe list.

        Both lists are merged into a single list suitable for allure report.
        Method returns the merged list.

        Returns:
            (list): Recipe as list of strings.
        """
        recipe_list = []
        # Merge both recipes.
        recipes = self.recipe_setup + self.recipe

        for rec in recipes:
            recipe_list.append(
                f'# device {rec["device"]}, start: {rec["start_t"]}, end: {rec["end_t"]}, exit_code: {rec["ec"]}\n'
                f'{rec["cmd"]}\n',
            )

        return recipe_list

    def mark_setup(self):
        """Move the recipe list into recipe_setup list.

        Method is called after the DUT device setup.
        It empties the recipe list afterwards.
        """
        self.recipe_setup = self.recipe
        self.recipe = []
