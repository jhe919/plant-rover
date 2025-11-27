import { useState } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Calendar, Filter, Download, ClipboardList } from 'lucide-react';

export function PlantHealthLog() {
  const [filterType, setFilterType] = useState('all');
  const [filterSeverity, setFilterSeverity] = useState('all');

  return (
    <div className="space-y-6">
      {/* Filters */}
      <Card className="p-6">
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-[#4CAF50]" />
            <h3>Filter Logs</h3>
          </div>
          <div className="flex flex-wrap gap-3">
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Issue Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Issues</SelectItem>
                <SelectItem value="Water Stress">Water Stress</SelectItem>
                <SelectItem value="Nutrient Deficiency">Nutrient Deficiency</SelectItem>
                <SelectItem value="Pest Detection">Pest Detection</SelectItem>
                <SelectItem value="Temperature Stress">Temperature Stress</SelectItem>
                <SelectItem value="Leaf Disease">Leaf Disease</SelectItem>
              </SelectContent>
            </Select>

            <Select value={filterSeverity} onValueChange={setFilterSeverity}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Severity" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Severities</SelectItem>
                <SelectItem value="critical">Critical</SelectItem>
                <SelectItem value="warning">Warning</SelectItem>
                <SelectItem value="info">Info</SelectItem>
              </SelectContent>
            </Select>

            <Button variant="outline" size="sm">
              <Calendar className="w-4 h-4 mr-2" />
              Date Range
            </Button>
            <Button variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
          </div>
        </div>
      </Card>

      {/* Empty State */}
      <Card className="p-12">
        <div className="flex flex-col items-center justify-center text-center">
          <div className="w-20 h-20 rounded-full bg-[#4CAF50]/10 flex items-center justify-center mb-4">
            <ClipboardList className="w-10 h-10 text-[#4CAF50]/50" />
          </div>
          <h3 className="mb-2">No Plant Health Logs</h3>
          <p className="text-muted-foreground max-w-md">
            Treatment logs and detected plant issues will appear here once the rover begins monitoring your field.
          </p>
        </div>
      </Card>
    </div>
  );
}
