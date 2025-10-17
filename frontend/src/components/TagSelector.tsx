import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Plus, X } from "lucide-react";
import { toast } from "sonner";

interface Tag {
  id: number;
  name: string;
  description?: string;
  color?: string;
}

interface TagSelectorProps {
  selectedTags: string[];
  onTagsChange: (tags: string[]) => void;
  availableTags: Tag[];
  onCreateTag: (name: string) => Promise<void>;
}

const TAG_VALIDATION = {
  MAX_TAGS: 10,
  MAX_TAG_LENGTH: 50,
  TAG_PATTERN: /^[a-zA-Z0-9_-]+$/,
};

export function TagSelector({
  selectedTags,
  onTagsChange,
  availableTags,
  onCreateTag,
}: TagSelectorProps) {
  const [newTagName, setNewTagName] = useState("");
  const [showDropdown, setShowDropdown] = useState(false);
  const [isCreatingTag, setIsCreatingTag] = useState(false);

  const validateTagName = (name: string): string | null => {
    if (!name.trim()) {
      return "Tag name cannot be empty";
    }
    if (name.length > TAG_VALIDATION.MAX_TAG_LENGTH) {
      return `Tag name must be ${TAG_VALIDATION.MAX_TAG_LENGTH} characters or less`;
    }
    if (!TAG_VALIDATION.TAG_PATTERN.test(name)) {
      return "Tag name can only contain alphanumeric characters, hyphens, and underscores";
    }
    if (availableTags.some((tag) => tag.name.toLowerCase() === name.toLowerCase())) {
      return "Tag already exists";
    }
    return null;
  };

  const handleAddTag = (tagName: string) => {
    if (selectedTags.length >= TAG_VALIDATION.MAX_TAGS) {
      toast.error(`Maximum ${TAG_VALIDATION.MAX_TAGS} tags allowed per tool`);
      return;
    }

    if (selectedTags.includes(tagName)) {
      toast.warning("Tag already added to this tool");
      return;
    }

    onTagsChange([...selectedTags, tagName]);
    setShowDropdown(false);
  };

  const handleRemoveTag = (tagName: string) => {
    onTagsChange(selectedTags.filter((t) => t !== tagName));
  };

  const handleCreateNewTag = async () => {
    const validationError = validateTagName(newTagName);
    if (validationError) {
      toast.error(validationError);
      return;
    }

    try {
      setIsCreatingTag(true);
      await onCreateTag(newTagName.trim());
      handleAddTag(newTagName.trim());
      setNewTagName("");
      toast.success(`Tag "${newTagName}" created successfully`);
    } catch (error) {
      toast.error("Failed to create tag");
      console.error("Error creating tag:", error);
    } finally {
      setIsCreatingTag(false);
    }
  };

  const availableTagsToAdd = availableTags.filter(
    (tag) => !selectedTags.includes(tag.name)
  );

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        {selectedTags.length === 0 ? (
          <p className="text-sm text-gray-500">No tags selected</p>
        ) : (
          selectedTags.map((tagName) => {
            const tag = availableTags.find((t) => t.name === tagName);
            return (
              <Badge
                key={tagName}
                variant="secondary"
                className="flex items-center gap-1 cursor-pointer hover:bg-secondary/80"
              >
                {tagName}
                <button
                  type="button"
                  onClick={() => handleRemoveTag(tagName)}
                  className="ml-1 hover:text-destructive focus:outline-none"
                  aria-label={`Remove ${tagName} tag`}
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            );
          })
        )}
      </div>

      <div className="space-y-2">
        <div className="relative">
          <div className="flex gap-2">
            <input
              type="text"
              value={newTagName}
              onChange={(e) => setNewTagName(e.target.value)}
              onFocus={() => setShowDropdown(true)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  if (availableTagsToAdd.some((t) => t.name === newTagName)) {
                    handleAddTag(newTagName);
                    setNewTagName("");
                  } else {
                    handleCreateNewTag();
                  }
                }
              }}
              placeholder="Type to search or create a new tag..."
              className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
              disabled={selectedTags.length >= TAG_VALIDATION.MAX_TAGS}
            />
            <Button
              type="button"
              onClick={handleCreateNewTag}
              disabled={!newTagName.trim() || isCreatingTag || selectedTags.length >= TAG_VALIDATION.MAX_TAGS}
              className="bg-primary hover:bg-primary/90 text-primary-foreground"
              size="sm"
            >
              {isCreatingTag ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <>
                  <Plus className="h-4 w-4 mr-1" />
                  Create
                </>
              )}
            </Button>
          </div>

          {showDropdown && availableTagsToAdd.length > 0 && newTagName.trim() && (
            <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-48 overflow-auto">
              {availableTagsToAdd
                .filter((tag) =>
                  tag.name.toLowerCase().includes(newTagName.toLowerCase())
                )
                .slice(0, 10)
                .map((tag) => (
                  <button
                    key={tag.id}
                    type="button"
                    onClick={() => {
                      handleAddTag(tag.name);
                      setNewTagName("");
                    }}
                    className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 focus:bg-gray-100 focus:outline-none"
                  >
                    <div className="font-medium">{tag.name}</div>
                    {tag.description && (
                      <div className="text-xs text-gray-500">{tag.description}</div>
                    )}
                  </button>
                ))}
            </div>
          )}
        </div>

        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>
            {selectedTags.length}/{TAG_VALIDATION.MAX_TAGS} tags selected
          </span>
          <span>Max {TAG_VALIDATION.MAX_TAG_LENGTH} characters per tag</span>
        </div>
      </div>
    </div>
  );
}
