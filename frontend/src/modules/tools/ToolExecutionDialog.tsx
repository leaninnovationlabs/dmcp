import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  CheckCircle,
  Download,
  RotateCcw,
  X,
  Play,
} from "lucide-react";

interface ToolParameter {
  name: string;
  type: string;
  description?: string;
  required: boolean;
  default?: string;
}

interface ExecutionResult {
  success: boolean;
  rows?: any[];
  rowCount?: number;
  executionTime?: number;
  error?: string;
}

interface ToolExecutionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  toolName?: string;
  toolDescription?: string;
  parameters?: ToolParameter[];
  parameterValues: Record<string, string>;
  onParameterChange: (name: string, value: string) => void;
  executionResult: ExecutionResult | null;
  executing: boolean;
  onExecute: () => void;
  onRunAgain: () => void;
  onClose: () => void;
  onExportCSV: () => void;
}

const ToolExecutionDialog = ({
  open,
  onOpenChange,
  toolName,
  toolDescription,
  parameters = [],
  parameterValues,
  onParameterChange,
  executionResult,
  executing,
  onExecute,
  onRunAgain,
  onClose,
  onExportCSV,
}: ToolExecutionDialogProps) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className="w-[800px] max-w-[90vw] sm:max-w-[800px] max-h-[65vh] flex flex-col"
        style={{ width: "800px", maxWidth: "90vw", maxHeight: "65vh" }}
      >
        <DialogHeader>
          <DialogTitle className="text-lg font-semibold">
            Execute Tool
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-3 flex-1 overflow-y-auto">
          {/* Tool Information */}
          <div className="bg-gray-50 rounded-lg p-4 space-y-1">
            <h3 className="font-semibold text-lg text-gray-900">
              {toolName}
            </h3>
            <p className="text-sm text-gray-700">{toolDescription}</p>
          </div>

          {/* Parameters Section - Only show when no execution result */}
          {!executionResult && (
            <div className="bg-gray-50 rounded-lg p-4">
              {parameters && parameters.length > 0 ? (
                <div className="space-y-4">
                  <h4 className="font-medium text-gray-900">Parameters</h4>
                  {parameters.map((param, index) => (
                    <div key={index} className="space-y-2">
                      <label className="text-sm font-medium text-gray-700">
                        {param.name}
                        {param.required && (
                          <span className="text-red-500 ml-1">*</span>
                        )}
                      </label>
                      <input
                        type="text"
                        value={parameterValues[param.name] || ""}
                        onChange={(e) => onParameterChange(param.name, e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-500 focus:border-gray-500"
                        placeholder={param.default || `Enter ${param.name}`}
                      />
                      {param.description && (
                        <p className="text-xs text-gray-500">
                          {param.description}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center space-y-2">
                  <div className="w-5 h-5 rounded-full bg-gray-600 flex items-center justify-center">
                    <span className="text-white text-xs font-bold">i</span>
                  </div>
                  <span className="text-sm text-gray-600">
                    This tool has no parameters to configure.
                  </span>
                </div>
              )}
            </div>
          )}

          {/* Execution Status */}
          {executionResult && (
            <div className="space-y-4">
              {executionResult.success ? (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <span className="font-medium text-green-800">
                      Execution Completed
                    </span>
                  </div>
                  <p className="text-sm text-green-700 mt-1">
                    {executionResult.rowCount} rows returned in{" "}
                    {executionResult.executionTime}ms
                  </p>
                </div>
              ) : (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2">
                    <X className="w-5 h-5 text-red-600" />
                    <span className="font-medium text-red-800">
                      Execution Failed
                    </span>
                  </div>
                  <p className="text-sm text-red-700 mt-1">
                    {executionResult.error}
                  </p>
                </div>
              )}

              {/* Results Section */}
              {executionResult.success && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-gray-900">Results</h4>
                    {executionResult.rows &&
                      executionResult.rows.length > 0 && (
                        <Button
                          onClick={onExportCSV}
                          className="bg-blue-600 hover:bg-blue-700 text-white flex items-center space-x-2"
                        >
                          <Download className="w-4 h-4" />
                          <span>Export CSV</span>
                        </Button>
                      )}
                  </div>

                  {executionResult.rows && executionResult.rows.length > 0 ? (
                    <div className="border border-gray-200 rounded-lg overflow-hidden">
                      <div className="overflow-x-auto max-h-[250px] overflow-y-auto">
                        <table className="w-full">
                          <thead className="bg-gray-50 sticky top-0 z-10">
                            <tr>
                              {Object.keys(executionResult.rows[0]).map(
                                (key) => (
                                  <th
                                    key={key}
                                    className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                  >
                                    {key}
                                  </th>
                                )
                              )}
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {executionResult.rows.map((row, index) => (
                              <tr key={index}>
                                {Object.values(row).map(
                                  (value, cellIndex) => (
                                    <td
                                      key={cellIndex}
                                      className="px-4 py-3 text-sm text-gray-900"
                                    >
                                      {String(value)}
                                    </td>
                                  )
                                )}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8 bg-gray-50 rounded-lg border border-gray-200">
                      <div className="flex flex-col items-center space-y-2">
                        <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center">
                          <span className="text-gray-600 text-sm font-bold">
                            !
                          </span>
                        </div>
                        <span className="text-gray-600 font-medium">
                          No records found
                        </span>
                        <span className="text-sm text-gray-500">
                          The query executed successfully but returned no
                          results.
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Loading State */}
          {executing && (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
              <span className="ml-3 text-gray-600">Executing tool...</span>
            </div>
          )}
        </div>

        <DialogFooter className="flex justify-end space-x-3 pt-4 pb-4 border-t border-gray-200 flex-shrink-0">
          {!executionResult ? (
            <>
              <Button
                variant="secondary"
                onClick={onClose}
                disabled={executing}
              >
                Cancel
              </Button>
              <Button
                onClick={onExecute}
                disabled={executing}
                className="bg-primary hover:bg-primary/90 text-primary-foreground flex items-center space-x-2"
              >
                <Play className="w-4 h-4" />
                <span>Execute Tool</span>
              </Button>
            </>
          ) : (
            <>
              <Button variant="secondary" onClick={onClose}>
                Close
              </Button>
              <Button
                onClick={onRunAgain}
                disabled={executing}
                className="bg-primary hover:bg-primary/90 text-primary-foreground border border-primary flex items-center space-x-2"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Run Again</span>
              </Button>
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ToolExecutionDialog;
