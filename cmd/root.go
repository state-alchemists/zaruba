package cmd

import (
	"github.com/spf13/cobra"
	"github.com/state-alchemists/zaruba/modules/logger"
)

var rootCmd = &cobra.Command{
	Use:   "zaruba <action> [...args]",
	Short: "Zaruba is agnostic generator and task runner",
	Long:  `Zaruba will help you create project and maintain dependencies among components`,
	Run: func(cmd *cobra.Command, args []string) {
		if len(args) < 1 {
			logger.Fatal("action required. Try `zaruba help`")
		}
	},
}

// Execute basic action
func Execute() {
	rootCmd.Execute()
}
